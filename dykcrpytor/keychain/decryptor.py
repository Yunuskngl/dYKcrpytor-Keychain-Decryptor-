# iOS keychain-2.db decrypt (protobuf + SSH keyclass unwrap).

import binascii
import os
import sqlite3
import subprocess
import time
from binascii import hexlify, unhexlify
from io import BytesIO
from struct import unpack

import pandas
from Crypto.Cipher import AES
from pyasn1.codec.der.decoder import decode

from dykcrpytor.proto import (
    SecDbKeychainSerializedAKSWrappedKey_pb2,
    SecDbKeychainSerializedItemV7_pb2,
    SecDbKeychainSerializedMetadata_pb2,
    SecDbKeychainSerializedSecretData_pb2,
)
from dykcrpytor.keychain.sqlite_export import export_decrypted_to_sqlite
from dykcrpytor.vendor import ccl_bplist


class KeychainDecryptor:
    def __init__(self, keychain_path):
        self.keychain_path = keychain_path
        self.progress_callback = None
        self.df_genp = None
        self.df_inet = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def _update_progress(self, message, value=None):
        if self.progress_callback:
            self.progress_callback(message, value)

    def _deserialize_data(self, rowitem):
        version = unpack("<L", rowitem["data"][0:4])[0]
        if version == 7:
            root = SecDbKeychainSerializedItemV7_pb2.SecDbKeychainSerializedItemV7()
            item = root.FromString(rowitem["data"][4:])
            rowitem["keyclass"] = item.keyclass
            encryptedSecretData_root = SecDbKeychainSerializedSecretData_pb2.SecDbKeychainSerializedSecretData()
            encryptedSecretData = encryptedSecretData_root.FromString(item.encryptedSecretData)
            SecDbKeychainSerializedAKSWrappedKey_root = (
                SecDbKeychainSerializedAKSWrappedKey_pb2.SecDbKeychainSerializedAKSWrappedKey()
            )
            encryptedSecretData_wrappedKey = SecDbKeychainSerializedAKSWrappedKey_root.FromString(
                encryptedSecretData.wrappedKey
            )
            rowitem["encryptedSecretData_wrappedKey"] = encryptedSecretData_wrappedKey.wrappedKey
            rowitem["encryptedSecretData_ciphertext"] = encryptedSecretData.ciphertext
            rowitem["encryptedSecretData_tamperCheck"] = encryptedSecretData.tamperCheck
            encryptedMetadata_root = SecDbKeychainSerializedMetadata_pb2.SecDbKeychainSerializedMetadata()
            encryptedMetadata = encryptedMetadata_root.FromString(item.encryptedMetadata)
            rowitem["encryptedMetadata_wrappedKey"] = encryptedMetadata.wrappedKey
            rowitem["encryptedMetadata_ciphertext"] = encryptedMetadata.ciphertext
            rowitem["encryptedMetadata_tamperCheck"] = encryptedMetadata.tamperCheck
        return rowitem

    def _unwrap_key(self, key, keyclass):
        if keyclass >= 6:
            ssh = subprocess.Popen(
                [
                    "sshpass",
                    "-p",
                    "alpine",
                    "ssh",
                    "-p2222",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "root@127.0.0.1",
                    "./keyclass_unwrapper",
                    hexlify(key).decode("ascii"),
                    str(int(keyclass)),
                ],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(0.1)
            out = ssh.stdout.readlines()
            while len(out) == 0:
                out = ssh.stdout.readlines()
                time.sleep(1)
            if len(out) > 0:
                unwrapped_key = out[0]
            else:
                print(
                    "error unwrapping key of keyclass {}: {} \n Trying again...".format(
                        keyclass, hexlify(key)
                    )
                )
                unwrapped_key = self._unwrap_key(key, keyclass)
        return unwrapped_key

    def _decrypt_secretData(self, item):
        if item["keyclass"] >= 6:
            unwrapped_key = self._unwrap_key(item["encryptedSecretData_wrappedKey"], item["keyclass"])
            bplist = BytesIO(item["encryptedSecretData_ciphertext"])
            plist = ccl_bplist.load(bplist)
            secretDataDeserialized = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
            authCode = secretDataDeserialized["root"]["SFAuthenticationCode"]
            iv = secretDataDeserialized["root"]["SFInitializationVector"]
            ciphertext = secretDataDeserialized["root"]["SFCiphertext"]

            gcm = AES.new(unhexlify(unwrapped_key)[:32], AES.MODE_GCM, iv)
            decrypted = gcm.decrypt_and_verify(ciphertext, authCode)

            der_data = decode(decrypted)[0]
            for k in der_data:
                if "Octet" in str(type(k[1])):
                    item["decrypted"].update({str(k[0]): bytes(k[1])})
                else:
                    item["decrypted"].update({str(k[0]): str(k[1])})
        return item

    def _decrypt_metadata(self, item, df_meta):
        if item["keyclass"] >= 6:
            bplist = BytesIO(item["encryptedMetadata_wrappedKey"])
            plist = ccl_bplist.load(bplist)
            metaDataWrappedKeyDeserialized = ccl_bplist.deserialise_NsKeyedArchiver(
                plist, parse_whole_structure=True
            )
            authCode = metaDataWrappedKeyDeserialized["root"]["SFAuthenticationCode"]
            iv = metaDataWrappedKeyDeserialized["root"]["SFInitializationVector"]
            ciphertext = metaDataWrappedKeyDeserialized["root"]["SFCiphertext"]
            unwrapped_metadata_key = self._unwrap_key(
                df_meta[df_meta.keyclass == int(item["keyclass"])].iloc[0].data,
                item["keyclass"],
            )
            gcm = AES.new(unhexlify(unwrapped_metadata_key)[:32], AES.MODE_GCM, iv)
            metadata_key = gcm.decrypt_and_verify(ciphertext, authCode)

            bplist = BytesIO(item["encryptedMetadata_ciphertext"])
            plist = ccl_bplist.load(bplist)
            metaDataDeserialized = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
            authCode = metaDataDeserialized["root"]["SFAuthenticationCode"]
            iv = metaDataDeserialized["root"]["SFInitializationVector"]
            ciphertext = metaDataDeserialized["root"]["SFCiphertext"]

            gcm = AES.new(metadata_key[:32], AES.MODE_GCM, iv)
            decrypted = gcm.decrypt_and_verify(ciphertext, authCode)
            der_data = decode(decrypted)[0]
            item["decrypted"] = {}
            for k in der_data:
                if "Octet" in str(type(k[1])):
                    item["decrypted"][str(k[0])] = bytes(k[1])
                else:
                    item["decrypted"][str(k[0])] = str(k[1])
        return item

    def decrypt(self):
        if not os.path.exists(self.keychain_path):
            raise IOError(f"Keychain bulunamadı: {self.keychain_path}")

        self._update_progress("Şifreli keychain okunuyor...", 0)
        db = sqlite3.connect(self.keychain_path)

        self._update_progress("Veriler yükleniyor...", 10)
        self.df_genp = pandas.read_sql_query("SELECT * FROM genp;", db)
        self.df_inet = pandas.read_sql_query("SELECT * FROM inet;", db)
        df_meta = pandas.read_sql_query("SELECT * FROM metadatakeys;", db)
        df_meta["keyclass"] = df_meta["keyclass"].astype(int)

        self._update_progress("Genel şifreler (genp) çözülüyor...", 20)
        self.df_genp["decrypted"] = self.df_genp.apply(lambda r: {"decrypted": {}}, axis=1)
        self.df_genp = self.df_genp.apply(lambda r: self._deserialize_data(r), axis=1)
        self.df_genp = self.df_genp.apply(lambda r: self._decrypt_metadata(r, df_meta), axis=1)
        self.df_genp = self.df_genp.apply(lambda r: self._decrypt_secretData(r), axis=1)

        self._update_progress("İnternet şifreler (inet) çözülüyor...", 50)
        self.df_inet["decrypted"] = self.df_inet.apply(lambda r: {"decrypted": {}}, axis=1)
        self.df_inet = self.df_inet.apply(lambda r: self._deserialize_data(r), axis=1)
        self.df_inet = self.df_inet.apply(lambda r: self._decrypt_metadata(r, df_meta), axis=1)
        self.df_inet = self.df_inet.apply(lambda r: self._decrypt_secretData(r), axis=1)

        db.close()
        self._update_progress("Tamamlandı!", 100)

        return self.get_decrypted_data()

    def get_decrypted_data(self):
        genp_list = self.df_genp["decrypted"].dropna().to_list() if self.df_genp is not None else []
        inet_list = self.df_inet["decrypted"].dropna().to_list() if self.df_inet is not None else []
        return {"genp": genp_list, "inet": inet_list}

    def export_to_sqlite(self, output_path, data=None):
        if data is None:
            data = self.get_decrypted_data()
        export_decrypted_to_sqlite(output_path, data)

#!/usr/bin/env python3

"""
Code copied from Professor Kenytt Avery's
https://gist.github.com/ProfAvery/15992d20962b52e04523419df4939ea6.

All credit goes to him.
"""

import os
import sys
import json

from jwcrypto import jwk


def generate_keys(key_ids: list[str]):
    keys = [jwk.JWK.generate(kid=key_id, kty="RSA", alg="RS256") for key_id in key_ids]
    print("Using key IDs: {}".format(key_ids))

    private_keys = [json.loads(exported) for exported in [key.export() for key in keys]]
    public_keys = [
        json.loads(exported)
        for exported in [key.export(private_key=False) for key in keys]
    ]

    print("Generating into ./run/jwt/{public,private}.json")
    os.makedirs("./run/jwt", exist_ok=True)

    private = open("./run/jwt/private.json", "w")
    json.dump({"keys": private_keys}, private, indent=2)

    public = open("./run/jwt/public.json", "w")
    json.dump({"keys": public_keys}, public, indent=2)


if __name__ == "__main__":
    key_id_file = open("jwt-key-id.txt", "r")
    key_ids = key_id_file.readlines()
    key_ids = [key_id.strip() for key_id in key_ids]
    generate_keys(key_ids)

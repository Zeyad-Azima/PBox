from Crypto.PublicKey import RSA

def generate_rsa_keys(key_size=2048):
    # Generate RSA key pair
    key = RSA.generate(key_size)

    # Export the private key in PEM format
    private_key = key.export_key(format='PEM')

    # Export the public key in PEM format
    public_key = key.publickey().export_key(format='PEM')

    return private_key, public_key

if __name__ == "__main__":
    private_key, public_key = generate_rsa_keys()

    # Save the private key to a file
    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key)

    # Save the public key to a file
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key)

    print("RSA keys generated and saved as 'private_key.pem' and 'public_key.pem'")

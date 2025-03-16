import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(["your_password_here"]).generate()
print(hashed_passwords)

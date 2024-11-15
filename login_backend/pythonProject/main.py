from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
import os

load_dotenv("admin_cred.env")


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app = FastAPI()

print(f"username : {ADMIN_USERNAME} and password : {ADMIN_PASSWORD}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LDAP_SERVER = 'ldap://localhost:389'
BASE_DN = 'dc=firstdomain,dc=com'


class Credentials(BaseModel):
    username: str
    password: str


def authenticate_user(username: str, password: str):

    user_details = None
    try:

        user_dn = f"cn={username},ou=employees,{BASE_DN}"
        print(f"Attempting to bind with user DN: {user_dn}")


        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=user_dn, password=password)


        if not conn.bind():
            raise HTTPException(status_code=401, detail="Invalid credentials")


        search_filter = f"(cn={username})"
        conn.search(
            search_base=BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['cn', 'sn', 'mail', 'mobile', 'title', 'uid']
        )


        if conn.entries:
            user_entry = conn.entries[0]
            user_details = {
                'commonName': user_entry.cn.value,
                'surName': user_entry.sn.value,
                'mail': user_entry.mail.value,
                'mobileNumber': user_entry.mobile.value if 'mobile' in user_entry else None,
                'title': user_entry.title.value if 'title' in user_entry else None,
                'uid': user_entry.uid.value,
            }
        else:
            raise HTTPException(status_code=404, detail="User not found in LDAP")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error during LDAP query: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred during LDAP query: {e}")
    finally:
        if conn and conn.bound:
            conn.unbind()

    return user_details


def get_all_users():
    all_users = []
    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=f"cn={ADMIN_USERNAME},{BASE_DN}", password=ADMIN_PASSWORD)
        if not conn.bind():
            raise HTTPException(status_code=401, detail="Admin authentication failed")


        conn.search(
            search_base=BASE_DN,
            search_filter="(objectClass=person)",
            search_scope=SUBTREE,
            attributes=['cn', 'sn', 'mail', 'mobile', 'title', 'uid']
        )


        for entry in conn.entries:
            all_users.append({
                'commonName': entry.cn.value,
                'surName': entry.sn.value,
                'mail': entry.mail.value,
                'mobileNumber': entry.mobile.value if 'mobile' in entry else None,
                'title': entry.title.value if 'title' in entry else None,
                'uid': entry.uid.value
            })
    except Exception as e:
        print(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving users")
    finally:
        if conn and conn.bound:
            conn.unbind()

    return all_users


@app.post("/login")
async def login(credentials: Credentials):

    username = credentials.username
    password = credentials.password

    print(f"credentials : {credentials.username}, {credentials.password}")


    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print(f"admin username : {ADMIN_USERNAME} AND PASSWORD : {ADMIN_PASSWORD}")
        users_list = get_all_users()
        print(users_list)
        return {"message": "Admin login successful", "is_admin": True}


    user_details = authenticate_user(username, password)

    return {
        "message": "Login successful",
        "user_details": user_details,
        "is_admin": False
    }


@app.post("/profile")
async def profile(credentials: Credentials):

    user_details = authenticate_user(credentials.username, credentials.password)
    print(user_details)
    return {"user_details": user_details}


@app.post("/users")
async def users(credentials: Credentials):
    if credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD:
        all_users = get_all_users()
        return {"users": all_users}
    else:
        raise HTTPException(status_code=403, detail="Access denied")


@app.post("/logout")
async def logout():

    return {"message": "User logged out successfully"}
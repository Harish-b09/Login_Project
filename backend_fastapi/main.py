from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ldap3 import Server, Connection, ALL, SUBTREE

app = FastAPI()

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

        user_dn = f"cn={username},cn=employees,{BASE_DN}"
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


@app.post("/login")
async def login(credentials: Credentials):
    username = credentials.username
    password = credentials.password

    user_details = authenticate_user(username, password)

    return {
        "message": "Login successful",
        "user_details": user_details
    }

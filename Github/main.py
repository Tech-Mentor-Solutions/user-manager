from fastapi import FastAPI
import uvicorn
import json
import pyrebase
from pydantic import BaseModel
from fastapi import HTTPException
from models import SignUpSchema,LogininSchema, UserSchema, TokenSchema
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
import firebase_admin
from firebase_admin import credentials,auth,firestore

app=FastAPI()

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceKey.json")
    firebase_admin.initialize_app(cred)
db=firestore.client()
firebaseConfig = {
  "apiKey": "AIzaSyCLtUwDOdhnZteJLEO0eAn4dlLTfO_JFVM",
  "authDomain": "demo1-5eaac.firebaseapp.com",
  "projectId": "demo1-5eaac",
  "storageBucket": "demo1-5eaac.appspot.com",
  "messagingSenderId": "541555533812",
  "appId": "1:541555533812:web:df9618882ac07906f83ba1",
  "measurementId": "G-678TGM8T2K",
  "databaseURL":""
}

firebase=pyrebase.initialize_app(firebaseConfig)

@app.post('/signup')
async def create_an_account(user_data:SignUpSchema):
    email=user_data.email
    password=user_data.password
    try:
        user=auth.create_user(
            email=email,
            password=password
        )
        return JSONResponse(content={"message": f"User account created successful {user.uid}"},status_code=201)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail="Account already exist {email}"
        )

@app.post('/login')
async def create_access_token(user_data:LogininSchema):
    email=user_data.email 
    password=user_data.password

    try:
        user=firebase.auth().sign_in_with_email_and_password(
            email=email,
            password=password
        )
        token=user['idToken']
        uid=validate_token(token)

        return JSONResponse(
            content={"token":token}, status_code=400
        )
    except KeyError:
        raise HTTPException(status_code=400, detail="Token not found in response")
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=f"ValueError: {ve}")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_detail = exc.errors()[0]
    error_msg = error_detail.get("msg", "An error occurred")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Field Missing: {error_msg}"}
    )   

# @app.post('/validate-token')
# async def validate_token(token_data: TokenSchema):
#     token = token_data.token

#     try:
#         # Verify the token
#         decoded_token = auth.verify_id_token(token)

#         # Extract UID and email from the decoded token
#         uid = decoded_token['uid']
#         email = decoded_token.get('email')

#         return JSONResponse(
#             content={"uid": uid, "email": email},
#             status_code=200
#         )
#     except auth.InvalidIdTokenError:
#         raise HTTPException(status_code=401, detail="Invalid ID token")
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=f"ValueError: {ve}")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Invalid Token")

# @app.post('/validate-token')
# async def validate_token(token_data: TokenSchema):
#     token = token_data.token

#     try:
#         # Verify the token
#         decoded_token = auth.verify_id_token(token)

#         # Extract UID and email from the decoded token
#         uid = decoded_token['uid']
#         email = decoded_token.get('email')
        
#         # Store user details in Firestore
#         user_ref = db.collection('users').document(uid)
#         user_ref.set({
#             'email': email,
#             'uid':uid,
#             'timestamp': firestore.SERVER_TIMESTAMP
#             # Add more user details as needed
#         })

#         return JSONResponse(
#             content={"uid": uid, "email": email},
#             status_code=200
#         )   
#     except auth.InvalidIdTokenError:
#         raise HTTPException(status_code=401, detail="Invalid ID token")
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=f"ValueError: {ve}")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Invalid Token")
@app.post('/validate-token')
async def validate_token(token_data: TokenSchema):
    token = token_data.token

    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)

        # Extract UID and email from the decoded token
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        
        # Get user data from request
        user_data = UserSchema(
            uid=uid,
            email=email,
            user_type="default",  # Set default user type
            name="",  # Set default name
            age=0,  # Set default age
            organization=""  # Set default organization
        )

        # Store user details in Firestore
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            'email': user_data.email,
            'uid': user_data.uid,
            'user_type': user_data.user_type,
            'name': user_data.name,
            'age': user_data.age,
            'organization': user_data.organization,
            'created_time': firestore.SERVER_TIMESTAMP,
            'modified_time': None  # Set as None initially
            # Add more user details as needed
        })

        return JSONResponse(
            content={"uid": user_data.uid, "email": user_data.email},
            status_code=200
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"ValueError: {ve}")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Token")  

@app.get("/get-all-user-emails")
async def get_all_user_emails():
    try:
        all_users = auth.list_users()
        emails = [user.email for user in all_users.iterate_all()]
        return {"emails": emails}
    except auth.AuthError as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/students")
# async def create_student(student: Student):
#     try:
#         # Add student to Firestore
#         doc_ref = db.collection('students').document()
#         doc_ref.set({
#             'name': student.name,
#             'age': student.age,
#             'grade': student.grade
#         })
#         return {"message": "Student profile created successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post('/ping')
async def validate_token(request:Request):
    headers=request.headers
    jwt=headers.get('token')
    user=auth.verify_id_token(jwt)
    return user.uid




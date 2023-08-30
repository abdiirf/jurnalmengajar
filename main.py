from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from config import get_database_connection
from mongonator import MongoClientWithPagination, ASCENDING, Paginate, DESCENDING
from urllib.parse import unquote
from pydantic import ValidationError
from pydantic import BaseModel
from bson import ObjectId
from typing import List


app = FastAPI()

# Establish MongoDB connection
client, db, guru_collection = get_database_connection("mongodb://localhost:27017/")
db = client["jurnalmengajar"]
guru_collection = db["guru"]

class Guru(BaseModel):
    id: str
    nama: str
    email: str
    password: str
    confirm_password: str
    nama_lengkap: str
    nama_panggilan: str
    jabatan: str
    alamat: str
    no_telp: str
    is_admin: bool

@app.get("/guru",  tags=[" guru"])
def get_guru_filtered(search: str = None, page: int = 1, limit: int = 5):
    query_filter = {}
    if search is not None:
        regex_pattern = f".*{search}.*"
        query_filter["$or"] = [
            {"nama": {"$regex": regex_pattern, "$options": "i"}}
        ]
    results = Paginate(collection=guru_collection, limit=limit, query=query_filter, projection={'nama': 1,'isAktif': 1} ,ordering_field="_id", ordering_case=ASCENDING, automatic_pagination=False).paginate()
    result1 = Paginate(collection=guru_collection, limit=limit, query=query_filter, projection={'nama': 1,'isAktif': 1} ,ordering_field="_id", ordering_case=ASCENDING, automatic_pagination=False, next_page=results.next_page).paginate()
    if page == 1:
        # Convert the results to a list
        results_list = list(results.response)
        all_jurnal = [
            {
                "nama": jurnal["nama"],
                "isAktif": jurnal["isAktif"],
            }
            for jurnal in results_list
        ]
        if not all_jurnal:
            return {"message": "Data  guru Kosong"}
        return all_jurnal
    else:
        # Convert the results to a list
        results_list = list(result1.response)
        all_jurnal = [
            {
                "nama": jurnal["nama"],
                "isAktif": jurnal["isAktif"]
            }
            for jurnal in results_list
        ]

        # Return the results
        if not all_jurnal:
            return {"message": "Data  guru Kosong"}
        return all_jurnal

@app.post("/guru", tags=["guru"])
def create_guru(nama: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), namalengkap: str = Form(...), namapanggilan: str = Form(...), jabatan: str = Form(...), alamat: str = Form(...), notelp: str = Form(...), isAdmin: bool = Form(...)):
    # Periksa apakah guru sudah ada dalam database
    existing_guru = guru_collection.find_one({"nama": nama})
    if existing_guru:
        raise HTTPException(status_code=400, detail="Guru sudah ada dalam database")

    guru = {
        "nama": nama,
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
        "namalengkap": namalengkap,
        "namapanggilan": namapanggilan,
        "jabatan": jabatan,
        "alamat": alamat,
        "notelp": notelp,
        "isAdmin": isAdmin,
    }
    id = guru_collection.insert_one(guru).inserted_id
    return {
        "_id": str(id),
        "nama": guru["nama"],
        "email": guru["email"],
        "password": guru["password"],
        "confirm_password": guru["confirm_password"],
        "namalengkap": guru["namalengkap"],
        "namapanggilan": guru["namapanggilan"],
        "jabatan": guru["jabatan"],
        "alamat": guru["alamat"],
        "notelp": guru["notelp"],
        "isAdmin": guru["isAdmin"],
    }

    
@app.patch("/guru/{nama}", tags=[" guru"])
def update_guru_by_nama(_guru: str, isAdmin: bool = Form(None)):
    # Decode the URL-encoded parameter
    nama = unquote(_guru)

    # Now you can use the decoded "nama" parameter in your database query
    guru = guru_collection.find_one({"nama": nama})
    if guru is None:
        raise HTTPException(status_code=404, detail=" guru tidak ditemukan")

    # Update data guru
    update_data = {}
    if isAdmin is not None:
        update_data["isAdmin"] = isAdmin

    guru.update(update_data)
    guru_collection.update_one({"nama": nama}, {"$set": update_data})

    return {
        "nama": guru["nama"],
        "isAdmin": guru["isAdmin"]
    }
@app.delete("/guru/{nama}", tags=[" guru"])
def delete_guru_by_nama(_guru: str):
    # Decode the URL-encoded parameter
    nama = unquote(_guru)

    # Now you can use the decoded "nama" parameter in your database query
    guru = guru_collection.find_one({"nama": nama})
    if guru is None:
        raise HTTPException(status_code=404, detail=" guru tidak ditemukan")
    
    guru_collection.delete_one({"nama": nama})
    return {" guru dihapus": guru["nama"]}

if __name__ == "__main__":
    app.run(debug=True)
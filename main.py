import json
from typing import Annotated
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
FILE = "products.json"



class ProductCreate(BaseModel):
    name: str 
    price: float 
    category: str | None = None
    in_stock: bool



class ProductUpdate(BaseModel):
    name: str 
    price: float 
    category: str | None = None
    in_stock: bool



class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str | None = None
    in_stock: bool



def read_products():
    with open(FILE, "r") as f:
        return json.load(f)


def save_products(products):
    with open(FILE, "w") as f:
        json.dump(products, f, indent=4)



@app.get("/products", response_model=list[ProductResponse])
def get_products(
    category: Annotated[str | None, Query(min_length=2)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    products = read_products()

    if category:
        result = []
        for product in products:
            if product["category"].lower() == category.lower():
                result.append(product)
        products = result

    return products[:limit]



@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: Annotated[int, Path(gt=0)]):
    products = read_products()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")



@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    products = read_products()

    new_product = product.model_dump()


    if len(products) == 0:
        new_product["id"] = 1
    else:
        new_product["id"] = products[-1]["id"] + 1

    products.append(new_product)
    save_products(products)
    return new_product



@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: Annotated[int, Path(gt=0)],
    product: ProductUpdate,
):
    products = read_products()

    for old_product in products:
        if old_product["id"] == product_id:
            old_product.update(product.model_dump())
            save_products(products)
            return old_product

    raise HTTPException(status_code=404, detail="Product not found")



@app.delete("/products/{product_id}")
def delete_product(product_id: Annotated[int, Path(gt=0)]):
    products = read_products()

    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            save_products(products)
            return {"message": "Product deleted successfully"}

    raise HTTPException(status_code=404, detail="Product not found")

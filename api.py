from fastapi import FastAPI, Response,HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr , validator
import database as db
import helpers # importamos la funcion del fichero helpers
from fastapi.responses import RedirectResponse
headers = {"content-type": "charset=utf-8"} # Para modificar los caracteres especiales

class ModeloCliente(BaseModel):
    dni: constr(min_length=8, max_length=8)
    nombre: constr(min_length=3, max_length=30)
    apellido: constr(min_length=3, max_length=30)

class ModeloCrearCliente(ModeloCliente): #Creamos una validacion par el dni
    @validator("dni")
    def validar_dni(cls,dni): # Definimos la funcion
        if helpers.dni_valido(dni, db.Clientes.lista): # Pasamos valores a validar
            return dni # Si es correcto crea el nuevo cliente
        raise ValueError("Cliente ya existente o DNI incorrecto") # Sino devuelve un mensaje de error   

app = FastAPI(
    title = " API de gestor de clientes",
    description= "Ofrece diferentes funciones para gestioanr los clientes."
) # Creando un app para que consuma la api


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/clientes/", tags=["Clientes"]) # Con este decorador indicamos que la funcion es una ruta de la api, utlizamos get por que es una funcion de consulta
async def clientes ():
    content = [cliente.to_dict() for cliente in db.Clientes.lista] # utlizamos la funcion creada en la base de datos
    return JSONResponse(content = content,headers=headers)

@app.get ("/clientes/buscar/{dni}", tags=["Clientes"]) # En esta ocacion escribirmos entre llaves un valor que se va a recuperar con ese nombre
async def clientes_buscar(dni:str):
    cliente = db.Clientes.buscar(dni=dni) # Recupera el cliente el valor de dni o en caso contrario none si no lo encuentra
    if not cliente :
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return JSONResponse (content= cliente.to_dict(),headers=headers) # Lo parseamos directamente

@app.post ("/clientes/crear/", tags=["Clientes"]) # definimos con metodo post para crear
async def clientes_crear(datos: ModeloCrearCliente ):
    cliente = db.Clientes.crear(datos.dni, datos.nombre, datos.apellido)
    if cliente:
        return JSONResponse (content= cliente.to_dict(),headers=headers)
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@app.put("/clientes/actualizar", tags=["Clientes"]) # Utilizamos put para actualizar informacion
async def clientes_actualizar(datos:ModeloCliente):
    if db.Clientes.buscar(datos.dni): # Buscamos el cliente a traves de su dni
        cliente = db.Clientes.modificar(datos.dni,datos.nombre,datos.apellido) # Si se encuentra se modifican los campos mencionados
        if cliente :
            return JSONResponse (content= cliente.to_dict(),headers=headers) # Y se parcea a diccionario
    raise HTTPException(status_code=404, detail="Cliente no encontrado") # Sino muestra mensaje de error

@app.delete("/clientes/borrar/{dni}/", tags=["Clientes"]) # Utilizamos delete para borrar registros
async def clientes_borrar(dni:str): # Recuperamos el dni como una cadena
    if db.Clientes.buscar(dni): # Buscamos el cliente a traves de su dni
        cliente = db.Clientes.borrar(dni=dni) # Recuperamos el valor a traves del borrado
        return JSONResponse (content= cliente.to_dict(),headers=headers) 
    raise HTTPException(status_code=404, detail="Cliente no encontrado") # Sino muestra mensaje de error



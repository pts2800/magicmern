#!/usr/bin/env python3
from pathlib import Path
import subprocess
import json

#creates server side files and structure
def fileStructure():
    print("INFO: ceating backend and front end folders")
    Path("backend").mkdir(exist_ok=True)
    Path("frontend").mkdir(exist_ok=True)
    Path("backend/src").mkdir(exist_ok=True)
    Path("backend/src/config").mkdir(exist_ok=True)
    Path("backend/src/controllers").mkdir(exist_ok=True)
    Path("backend/src/routes").mkdir(exist_ok=True)
    Path("backend/src/models").mkdir(exist_ok=True)
    Path("backend/src/middleware").mkdir(exist_ok=True)

    Path("backend/.env").touch()
    Path("backend/src/server.js").touch()
    Path("backend/src/config/db.js").touch()
    Path("backend/src/controllers/thingsController.js").touch()
    Path("backend/src/models/Things.js").touch()
    Path("backend/src/routes/thingsRoutes.js").touch()
    Path("backend/src/middleware/mwApiResponse.js").touch()

def installnpm():
    print("INFO: installing npm files")
    print("INFO: running init")
    subprocess.run(["npm.cmd", "init", "-y"],cwd="backend",check=True)
    print("INFO: installing express")
    subprocess.run(["npm.cmd", "install", "express"], cwd="backend", check=True)
    print("INFO: installing mongoose")
    subprocess.run(["npm.cmd", "install", "mongoose"],cwd="backend",check=True)
    print("INFO: installing nodemon")
    subprocess.run(["npm.cmd", "install", "nodemon", "-D"], cwd="backend", check=True)
    print("INFO: installing dotenv")
    subprocess.run(["npm.cmd", "install", "dotenv"], cwd="backend", check=True)

def modFiles():
    print("INFO: adding info to files")
    modEnv() #add .env info
    modPackage()
    modServer()
    modConfig()
    modControllers()
    modModels()
    modRoutes()
    modMiddleware()

#creates basic .env file
def modEnv():
    file = Path("backend/.env")
    file.write_text("""\
MONGO_DB_URL=mongodb://192.168.1.163:27017/things_db
PORT=5001
    """)

def modPackage():
    file = Path("backend\package.json")
    fileText = json.loads(file.read_text())
    fileText["main"] = "src/server.js"
    fileText["scripts"]["dev"] = "nodemon server.js"
    fileText["scripts"]["production"] = "node server.js"
    fileText["type"] = "module"
    file.write_text(json.dumps(fileText,indent=2)+"\n")

def modServer():
    file = Path("backend\src\server.js")
    file.write_text("""\
import express from "express";
import thingsRoutes from "./routes/thingsRoutes.js";
//looks for exported functions in db.js
import { connectDB } from "./config/db.js";
import dotenv from "dotenv";
import apiResponse from "./middleware/mwApiResponse.js";

//allows for use of .env file
dotenv.config();

const app = express();
//if port is undefined, will default to 5001
const PORT = process.env.PORT || 5001

//middleware = before response is sent back to client, do something
app.use(express.json()); //parses json

//custom middleware
app.use(apiResponse)

//endpoints - if api call uses /api/things using thingRoutes
app.use("/api/things", thingsRoutes);
//app.use("/api/settings",settingsRoutes)

//connects to DB before services start
connectDB().then(() => {
    //sets port
    app.listen(PORT, ()=> {
    console.log("Server started on PORT: ",PORT);
    });
});
    """)

def modConfig():
    file = Path("backend\src\config\db.js")
    file.write_text("""\
import mongoose from "mongoose"

//connects to DB
export const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_DB_URL);
        console.log("INFO: mongodb connected successfully");
    }catch (error) {
        console.log("ERROR: error connecting to mongodb",error);
        process.exit(1); //exit with failure
    }
}
    """)

def modControllers():
    file = Path("backend/src/controllers/thingsController.js")
    file.write_text("""\
import { connect } from "mongoose"
import Things from "../models/Things.js"

export async function getThings(req, res){
    //*interact with DB*
    try {
        const things = await Things.find().sort({createdAt:-1}); //sort by newest first
        res.status(200).json(things)
    } catch (error){
        console.error("Error getThings controller", error)
        res.status(500).json({message:"Internal Server Error"})
    }
}
export async function getOneThings(req, res){
    try{
        const thing = await Things.findById(req.params.id);
        if (!thing) return res.status(404).json({message: "WARNING: id not found"});
        res.json(thing);
    } catch (error){
        console.error("ERROR: could not get ID", error);
        res.status(500).json({message: "ERROR: internal server error"});
    }
}
export async function newThings(req, res){
    //*interact with DB*
    try{
        const {name,location} = req.body;
        const newThings = new Things({name:name, location:location})
        await newThings.save()
        res.status(201).json({message:"INFO: thing added successfully"})
    }catch (error) {
        console.error("ERROR: error in newThings controller",error)
    }
}
export async function updateThings(req, res){
    //*interact with DB*
    try {
        const {name,location} = req.body
        //.id is used because of the :id in the api call
        const updatedThing = await Things.findByIdAndUpdate(
            req.params.id, 
            {name,location},
        {
            new: true,
        });
        if(!updatedThing) return res.status(404).json({message:"WARNING: ID not found"})
        res.status(200).json({updatedThing})
    } catch (error){
        console.error("ERROR: updateThings in thingsController.js", error)
        res.status(500).json({message:"ERROR: internal server error"})
    }
}
export async function deleteThings(req, res){
    try{
        const deletedThings = await Things.findByIdAndDelete(req.params.id);
        if(!deletedThings) return res.status(404).json({message:"WARNING: id not found"});
        res.json({message:"INFO: ID deleted successfully"})
    } catch (error) {
        console.error("ERROR: controllers/thingsControllers.js/deleteThings could not delete ID ", error)
        res.status(500).json({message:"ERROR: controller: thingsController.js: deleteThings"})
    }
}
    """)

def modModels():
    file = Path("backend/src/models/Things.js")
    file.write_text("""\
import mongoose from "mongoose";

const thingsSchema = new mongoose.Schema({
    name: {
        type:String,
        required: true
    },
    location: {
        type:String,
        required: true
    },
},
//timestamp is broken - need to fix it
{ timestamps: true }
);

const Things = mongoose.model("Things", thingsSchema);
export default Things;
    """)

def modRoutes():
    file = Path("backend/src/routes/thingsRoutes.js")
    file.write_text("""\
import express from "express";
import { getThings, getOneThings, newThings, updateThings, deleteThings } from "../controllers/thingsController.js";

const router = express.Router();

//when get is called, finds function getThings in thingsController.js
router.get("/", getThings)
router.get("/:id", getOneThings)
router.post("/", newThings)
router.put("/:id", updateThings)
router.delete("/:id", deleteThings)

export default router;
    """)

def modMiddleware():
    file = Path("backend/src/middleware/mwApiResponse.js")
    file.write_text("""\
const apiResponse = async (req,res,next) => {
    console.log(`INFO: sending API response for ${req.method} ${req.url}`);
    //finishes the res, could be API result
    next();
}

export default apiResponse;
    """)

#PICK YOUR POISON
def main():
    print("MAKE SURE YOU ARE IN YOUR PROJECT FOLDER BEFORE YOU START SCRIPT")
    print("HAS ONLY BEEN TESTED ON WINDOWS")
    useros = int(input("1 for windows, 2 for linux: "))
    if useros == 1:
        fileStructure()
        installnpm()
        modFiles()
    elif useros == 2:
        print("didn't you read this has only been tested on windows?")
    else:
        print("you failed at entering 1 or 2, try again")

main()

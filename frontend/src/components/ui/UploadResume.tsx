import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import axios from "axios";
import { useState,useEffect } from "react"


export function UploadResume() {
    const [file, setfile] = useState< File | null > (null);
    const [buttonText, setButtonText] = useState("Upload plss ....")
    const [userJob, setuserJob] = useState("")

    //to take the input in the file varibale 
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected_file = e.target.files?.[0] ?? null;
      setfile(selected_file)
      setButtonText("pls wait ...");
    };

    const handleUpload = async() => {
      if (!file){
        console.log("pls give a file");
        return;
      }
      const formData = new FormData();
      formData.append("uploaded_file", file);
      try {
      const res = await axios.post("http://localhost:8000/resume/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        withCredentials:true,
      })
      8
      console.log("upload succesfull", res.data);
      setButtonText("go to the next page")

      
      } catch(err){
          console.log("upload failed", err);
      }

    }


  return (
    <div className="grid w-full max-w-sm items-center gap-3">
      <Label htmlFor="picture">Picture</Label>
      <Input id="picture" type="file" onChange={handleFileChange}/>
      <button
      onClick={handleUpload}
      className="bg-blue-500 text-white rounded px-4 py-2 mt-2"
      >
        {buttonText}

      </button>
    
      
    </div>
  )
}

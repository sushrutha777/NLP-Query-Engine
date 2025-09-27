import React from "react";
import axios from "axios";

export default function DocumentUploader({onIndexed}){
  const [files, setFiles] = React.useState(null);
  const [msg, setMsg] = React.useState("");

  const upload = async () => {
    if(!files || files.length===0) { setMsg("Select files"); return; }
    const form = new FormData();
    for(let i=0;i<files.length;i++) form.append("files", files[i]);
    setMsg("Uploading...");
    try{
      const res = await axios.post("http://localhost:8000/api/ingest/documents", form, {
        headers: {"Content-Type":"multipart/form-data"}
      });
      setMsg("Uploaded: "+(res.data.total_indexed || 0));
      onIndexed(res.data);
    } catch(e){
      setMsg("Error: "+(e.response?.data?.detail || e.message));
    }
  };

  return (
    <div style={{border:"1px solid #ddd", padding:12, borderRadius:8, marginTop:12}}>
      <h3>Document Uploader</h3>
      <input type="file" multiple onChange={(e)=>setFiles(e.target.files)} />
      <div style={{marginTop:8}}>
        <button onClick={upload}>Upload & Index</button>
      </div>
      <div style={{marginTop:8,color:"#555"}}>{msg}</div>
      <div style={{marginTop:8,fontSize:12,color:"#777"}}>Supported: .txt .csv .pdf .docx</div>
    </div>
  );
}

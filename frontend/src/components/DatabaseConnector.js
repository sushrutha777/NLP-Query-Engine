import React from "react";
import axios from "axios";

export default function DatabaseConnector({onSchema}){
  const [connStr, setConnStr] = React.useState("sqlite:///company_demo.db");
  const [msg, setMsg] = React.useState("");

  const connect = async () => {
    setMsg("Connecting...");
    try{
      const form = new FormData();
      form.append("connection_string", connStr);
      const res = await axios.post("http://localhost:8000/api/ingest/database", form);
      if(res.data.schema){
        setMsg("Connected & schema discovered.");
        onSchema(res.data.schema);
      } else {
        setMsg("Connected (no schema returned).");
      }
    } catch(e){
      setMsg("Error: "+(e.response?.data?.detail || e.message));
    }
  };

  return (
    <div style={{border:"1px solid #ddd", padding:12, borderRadius:8, marginBottom:12}}>
      <h3>Database Connector</h3>
      <div>
        <input value={connStr} onChange={e=>setConnStr(e.target.value)} style={{width:"100%",padding:8}} />
      </div>
      <div style={{marginTop:8}}>
        <button onClick={connect}>Connect & Analyze</button>
      </div>
      <div style={{marginTop:8,color:"#555"}}>{msg}</div>
    </div>
  );
}

import React from "react";
import axios from "axios";

export default function QueryPanel({onResult}){
  const [q, setQ] = React.useState("");
  const [msg, setMsg] = React.useState("");
  const [history, setHistory] = React.useState([]);

  const submit = async () => {
    if(!q) return;
    setMsg("Querying...");
    const form = new FormData();
    form.append("query", q);
    try{
      const res = await axios.post("http://localhost:8000/api/query", form);
      setMsg("Done in "+(res.data.time || 0)+"s");
      onResult(res.data);
      setHistory(h=>[q].concat(h).slice(0,10));
    } catch(e){
      setMsg("Error: "+(e.response?.data?.detail || e.message));
    }
  };

  return (
    <div style={{border:"1px solid #ddd", padding:12, borderRadius:8}}>
      <h3>Query</h3>
      <input value={q} onChange={e=>setQ(e.target.value)} style={{width:"100%",padding:8}} placeholder="e.g. Show me all Python developers in Engineering" />
      <div style={{marginTop:8}}>
        <button onClick={submit}>Run Query</button>
      </div>
      <div style={{marginTop:8,color:"#555"}}>{msg}</div>
      <div style={{marginTop:12}}>
        <strong>History:</strong>
        <ul>
          {history.map((h,i)=><li key={i}><button style={{marginRight:8}} onClick={()=>setQ(h)}>{h}</button></li>)}
        </ul>
      </div>
    </div>
  );
}

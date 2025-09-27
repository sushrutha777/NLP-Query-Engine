import React from "react";
import DatabaseConnector from "./components/DatabaseConnector";
import DocumentUploader from "./components/DocumentUploader";
import QueryPanel from "./components/QueryPanel";
import ResultsView from "./components/ResultsView";
import axios from "axios";

export default function App(){
  const [schema, setSchema] = React.useState(null);
  const [results, setResults] = React.useState(null);
  const [status, setStatus] = React.useState({indexed:0});

  React.useEffect(() => {
    axios.get("http://localhost:8000/api/schema").then(r=>setSchema(r.data)).catch(()=>{});
    axios.get("http://localhost:8000/api/ingest/status").then(r=>setStatus(r.data)).catch(()=>{});
  }, []);

  return (
    <div style={{fontFamily:"sans-serif",padding:20}}>
      <h1>NLP Query Engine — Demo</h1>
      <div style={{display:"flex", gap:20, alignItems:"flex-start"}}>
        <div style={{flex:1, maxWidth:420}}>
          <DatabaseConnector onSchema={(s)=>setSchema(s)} />
          <DocumentUploader onIndexed={(st)=>setStatus(st)} />
          <div style={{marginTop:20}}>
            <strong>Ingestion Status:</strong> {status.indexed} docs indexed.
          </div>
          <div style={{marginTop:20}}>
            <strong>Discovered Schema (preview):</strong>
            <pre style={{height:220,overflow:"auto",background:"#f6f6f6",padding:8}}>
              {schema ? JSON.stringify(schema, null, 2) : "No schema discovered yet."}
            </pre>
          </div>
        </div>
        <div style={{flex:2}}>
          <QueryPanel onResult={(r)=>setResults(r)} />
          <ResultsView results={results} />
        </div>
      </div>
    </div>
  );
}

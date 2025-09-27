import React from "react";

export default function ResultsView({results}){
  if(!results) return <div style={{marginTop:12}}>No results yet.</div>;
  const {result, from_cache, query_type, time} = results;
  return (
    <div style={{marginTop:12, border:"1px solid #ddd", padding:12, borderRadius:8}}>
      <div><strong>Type:</strong> {query_type} <strong>Time:</strong> {time}s {from_cache?"(cache)":""}</div>
      <hr />
      {result.sql ? (
        <div>
          <h4>Database results</h4>
          {result.sql.error ? <div style={{color:"red"}}>{result.sql.error}</div> : (
            <div style={{overflowX:"auto"}}>
              <table style={{width:"100%",borderCollapse:"collapse"}}>
                <thead>
                  <tr>
                    {result.sql.length>0 && Object.keys(result.sql[0]).map((c,i)=><th key={i} style={{border:"1px solid #ddd",padding:6}}>{c}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {result.sql.map((row,ri)=>
                    <tr key={ri}>
                      {Object.values(row).map((v,ci)=><td key={ci} style={{border:"1px solid #eee",padding:6}}>{String(v)}</td>)}
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : null}
      {result.docs ? (
        <div>
          <h4>Document results</h4>
          {result.docs.length===0 ? <div>No documents matched.</div> :
            result.docs.map((d,i)=>
              <div key={i} style={{border:"1px solid #eee", padding:8, marginBottom:8}}>
                <div><strong>{d.filename}</strong> (score: {d.score.toFixed(4)})</div>
                <div style={{color:"#555"}}>{d.snippet}</div>
              </div>
            )
          }
        </div>
      ) : null}
    </div>
  );
}

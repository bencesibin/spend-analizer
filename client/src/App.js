import logo from './logo.svg';
import './App.css';
import axios from "axios";
import React from 'react';
import Statements from './component/statements';

function App() {

  const [uniqueRefIds, setUniqueRefIds] = React.useState(null);
  const [uniqueRefIdStatement, setUniqueRefIdStatement] = React.useState(null);
  const [uniqueRefIdTotal, setUniqueRefIdTotal] = React.useState(null);

  React.useEffect(() => {
    axios.get('http://127.0.0.1:5000/get_statements_unique_ref_id').then((response) => {
      console.log(response.data.data);
      setUniqueRefIds(response.data.data);
    });
  }, []);

  const handleUniqueRefIdDoubleClick = (uniqueRefId) => {
    axios.get(`http://127.0.0.1:5000/get_statements_ref_id?ref_id=${uniqueRefId}`).then((response) => {
      console.log(response.data.data);
      setUniqueRefIdStatement(response.data.data);
      setUniqueRefIdTotal(response.data.total_amount);
    });
    console.log('uniqueRefId : ', uniqueRefId);
  };

  const handleDoubleClick = () => {
    console.log('handleDoubleClick catched');
  };

  const handleDoubleDropALL = () => {
    axios.get('http://127.0.0.1:5000/drop_table').then((response) => {
      console.log(response.data.data);
    });
  };

  const handleDoubleCreateTable = () => {
    axios.get('http://127.0.0.1:5000/create_table').then((response) => {
      console.log(response.data.data);
    });
  };

  const handleDoubleFill = () => {
    axios.get('http://127.0.0.1:5000/insert_data_form_pdf').then((response) => {
      console.log(response.data.data);
    });
  };

  if (!uniqueRefIds) return null;


  return (
    <div className="App">
      <header className="App-header">
        <div>
          <button onDoubleClick={handleDoubleClick}>Test Click me</button>
          <button onDoubleClick={handleDoubleDropALL}>DropALL</button>
          <button onDoubleClick={handleDoubleCreateTable}>CreateTable</button>
          <button onDoubleClick={handleDoubleFill}>Fill</button>
          <ul >
            {uniqueRefIds.map((uniqueRefId, i) => {
              if (!uniqueRefId) return null
              return (
                <li key={i} > {uniqueRefId} <button onDoubleClick={() => handleUniqueRefIdDoubleClick(uniqueRefId)}>get statement</button></li>
              )
            })}
          </ul>
        </div>
        hello
        <Statements
          uniqueRefIdStatement={uniqueRefIdStatement}
          uniqueRefIdTotal={uniqueRefIdTotal}
        />
      </header >
    </div >
  );
}

export default App;

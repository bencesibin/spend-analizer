import logo from './logo.svg';
import './App.css';
import axios from "axios";
import React from 'react';

function App() {

  const [post, setPost] = React.useState(null);

  React.useEffect(() => {
    axios.get('http://127.0.0.1:5000/get_statements').then((response) => {
      console.log(response.data.data);
      setPost(response.data.data);
    });
  }, []);

  if (!post) return null;

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <table>
            <thead>
              <tr>
                {/* <td>id</td> */}
                <td>file_name</td>
                {/* <td>whole_line</td> */}
                <td>ref</td>
                <td>date</td>
                {/* <td>disc</td> */}
                <td>amount</td>
                <td>type</td>
              </tr>
            </thead>
            <tbody>
              {post.map((row, i) => {
                if (!row.ref) return null
                return (
                  <tr key={i}>
                    <td>{row.file_name}</td>
                    <td>{row.ref}</td>
                    <td>{new Date(row.date).toLocaleDateString()}</td>
                    {/* <td>{row.disc}</td> */}
                    <td>{row.amount}</td>
                    <td>{row.type}</td>
                  </tr>)
              })}

            </tbody>
          </table>
        </div>
      </header >
    </div >
  );
}

export default App;

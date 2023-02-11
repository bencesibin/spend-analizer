import React from 'react';

export default function Statements({ uniqueRefIdStatement, uniqueRefIdTotal }) {

  if (!uniqueRefIdTotal) return null

  return (
    <div>
      total : {uniqueRefIdTotal}
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
          {uniqueRefIdStatement?.map((row, i) => {
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
  )
}

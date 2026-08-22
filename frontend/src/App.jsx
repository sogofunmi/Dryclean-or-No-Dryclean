import './App.css';
import {BrowserRouter as Router, Routes, Route} from "react-router-dom"
import FabricComponents from "./components/FabricComp.jsx";
import ItemDescription from "./components/ItemDesc.jsx";

function App() {

  return (
    <Router>
      <div className="app-container">
        <header>
          <h1>Care Label Prediction</h1>
        </header>
        <main>
          <Routes>
            <Route path={"/*"} element={<ItemDescription />} />
            <Route path={"/composition/*"} element={<FabricComponents />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

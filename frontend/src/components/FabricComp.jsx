import {useState} from "react";
import {useLocation, Link} from 'react-router-dom';
import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL;

function FabricComponents() {
    const location = useLocation();
    const receivedData = location.state?.itemDetails || {description: "", price: ""};
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [prediction, setPrediction] = useState(null)

    const fabrics = [
        {id: "acetate", title: "Acetate", text: "Diacetate, Triacetate"},
        {id: "acrylic", title: "Acrylic", text: "Modacrylic"},
        {id: "cotton", title: "Cotton", text: "Denim, Circulose, Cupro"},
        {id: "elastane", title: "Elastane", text: "Spandex, Lycra"},
        {id: "leather", title: "Leather", text: "Suede, Lambskin, Cowskin, Calfskin"},
        {id: "linen", title: "Linen", text: "Hemp, Flax"},
        {id: "lyocell", title: "Lyocell", text: "Tencel, Microtencel"},
        {id: "modal", title: "Modal", text: ""},
        {id: "polyamide", title: "Polyamide", text: "Nylon"},
        {id: "polyester", title: "Polyester", text: "Faux fur, Faux leather"},
        {id: "silk", title: "Silk", text: "Seta"},
        {id: "wool", title: "Wool", text: "Merino, Angora, Mohair, Alpaca, Cashmere, Yak, Agnello"},
        {id: "other", title: "Other", text: "Metal, Glass"},
        {id: "viscose", title: "Viscose", text: "Rayon"}

    ];
    
    const [pctValue, setPctValue] = useState(() => {
        const initialValue = {};
        fabrics.forEach(fabric => {
            initialValue[fabric.id] = "";
        });
        return initialValue
    });

    const totalValue = Object.values(pctValue).reduce((sum, value) => {
        return sum + (parseFloat(value, 10) || 0)
    }, 0);

    const isHundred = totalValue === 100;

    function handlePct (id, value) {
        if (value === "") {
            setPctValue(prev => ({...prev, [id]: ""}))
            return;
        }

        const intVal = parseFloat(value, 10);
        if (!isNaN(intVal)) {
            setPctValue(prev => ({...prev, [id]: intVal}))
        }
    }

    async function makePrediction() {
        if (!isHundred) return;
        setLoading(true)

        const givenComposition = {};
        Object.keys(pctValue).forEach(id => {
            if (pctValue[id] != "") {
                givenComposition[id] = pctValue[id]
            }
        })


        const finalData = {
            description: receivedData.description,
            price: parseFloat(receivedData.price, 10),
            composition: givenComposition
        }

        console.log(finalData);
        try {
            const response = await axios.post(`${API_URL}/api`, finalData);
            setPrediction(response.data.prediction);
        } catch (error) {
            setPrediction("Error making prediction.");
        } finally {
            setLoading(false);
        }
    }
    return (
        
    <div>
        
        <h2>Fabric Names</h2>
        <h4>All given percentages must add up to 100</h4>
        <div className="fabric-grid">
            {fabrics.map(fabric => {
                
                return (
                    <div
                        key={fabric.id} 
                        className="fabric-card"
                        >
                    <h3>{fabric.title}</h3>
                    <p>{fabric.text}</p>
                    
                        <div>
                            <label>
                                Enter Percentage
                            </label>
                            <input
                                type="number"
                                placeholder="0"
                                min="1"
                                max="100"
                                step="any"
                                value={pctValue[fabric.id]}
                                onChange={(e) => handlePct(fabric.id, e.target.value)}/>
                        </div>
                    
                    </div> 
                )
            })}
        </div>
        <div className="navigation-container">
            <Link to="/" className="btn-button">
                Back
            </Link>
        
            <button className="btn-button" onClick={makePrediction}
            disabled={loading || !isHundred}>Predict</button>
        </div>
        {prediction && (
            <div className="predict">
                Care prediction: {prediction}
            </div>
        )}

        
    </div>
    )
}

export default FabricComponents
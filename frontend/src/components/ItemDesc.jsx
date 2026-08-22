import {useState} from "react";
import {useNavigate} from "react-router-dom";

function ItemDescription() {
    const navigate = useNavigate();
    const [error, setError] = useState(null);
    const [itemDetails, setItemDetails] = useState({description: "", price: ""})

    function itemDetailsChange (item, value) {
        setItemDetails(prev => ({...prev, [item]:value}));
    }

    const {description, price} = itemDetails
    const handleSubmit = (e) => {
        e.preventDefault();
        
        setError("");
        navigate("/composition", {state: {itemDetails}});
    };

    return (
    <form onSubmit={handleSubmit} className="form-layout">
        <div className="form-row">
            <div className="descr-container">
                <label> Brief clothing description</label>
                <input
                    type="text"
                    placeholder="Midi Beaded Pencil Skirt"
                    value={itemDetails.description}
                    onChange={(e) => itemDetailsChange("description", e.target.value)}/>
            </div>
            <div className="descr-container">
                <label>Enter Price</label>
                <input 
                    type="number"
                    placeholder="0"
                    min="1"
                    value={itemDetails.price}
                    onChange={(e) => itemDetailsChange("price", e.target.value)}/>
            </div>
        </div>
        <div className="form-actions">
            <button disabled={!description.trim() || !price} className="btn-button" type="submit">Next: Fabric Composition</button>
        </div>
    </form>
    )
}

export default ItemDescription
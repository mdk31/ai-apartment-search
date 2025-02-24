import { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function RentalApp() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [llmCode, setLlmCode] = useState("");
  const [explanation, setExplanation] = useState("");
  const [saveQuery, setSaveQuery] = useState(false);

  const handleSearch = async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, saveQuery }),
    });

    const data = await response.json();
    setResults(data.results);
    setLlmCode(data.code);
    setExplanation(data.explanation);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">NYC Rental Search</h2>
        </CardHeader>
        <CardContent>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your apartment criteria..."
            className="w-full p-2 border rounded"
          />
          <div className="flex items-center mt-2">
            <Checkbox checked={saveQuery} onCheckedChange={(checked) => setSaveQuery(checked)} />
            <label className="ml-2">Allow data to improve the model</label>
          </div>
          <Button onClick={handleSearch} className="mt-4 w-full">
            Search
          </Button>
        </CardContent>
      </Card>

      {llmCode && (
        <Card className="mt-4">
          <CardHeader>
            <h3 className="text-lg font-semibold">LLM Generated Code</h3>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-200 p-2 rounded text-sm overflow-auto">{llmCode}</pre>
            <p className="mt-2 text-sm">{explanation}</p>
          </CardContent>
        </Card>
      )}

      {results.length > 0 && (
        <MapContainer center={[40.7128, -74.006]} zoom={12} className="h-80 w-full mt-4">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          {results.map((res, idx) => (
            <Marker key={idx} position={[res.lat, res.lng]}>
              <Popup>{res.name}</Popup>
            </Marker>
          ))}
        </MapContainer>
      )}
    </div>
  );
}
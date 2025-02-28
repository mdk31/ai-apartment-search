"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchApartments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/search`, { params: { query } });
      setResults(response.data);
    } catch (error) {
      console.error("Error fetching results:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-6">
      <h1 className="text-3xl font-bold">Find Your Perfect NYC Apartment</h1>
      <p className="mt-2 text-gray-600">Enter criteria like "2-bedroom near Central Park under $3000".</p>

      <div className="mt-4 w-full max-w-md">
        <input
          type="text"
          className="w-full p-3 border rounded-lg focus:outline-none focus:ring focus:border-blue-400"
          placeholder="Search for apartments..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="mt-2 w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
          onClick={searchApartments}
        >
          Search
        </button>
      </div>

      {/* Loading Indicator */}
      {loading && <p className="mt-4 text-gray-500">Loading results...</p>}

      {/* Display Results */}
      <div className="mt-6 w-full max-w-lg">
        {results.length > 0 ? (
          <ul className="space-y-4">
            {results.map((apartment, index) => (
              <li key={index} className="p-4 border rounded-lg shadow">
                <h2 className="text-lg font-semibold">{apartment.title}</h2>
                <p className="text-gray-600">{apartment.location}</p>
                <p className="text-gray-800 font-bold">${apartment.price}/month</p>
              </li>
            ))}
          </ul>
        ) : (
          !loading && <p className="mt-4 text-gray-500">No results found.</p>
        )}
      </div>
    </main>
  );
}

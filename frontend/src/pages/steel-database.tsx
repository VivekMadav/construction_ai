import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Upload, Database, Search, FileText, Calculator, ArrowLeft } from 'lucide-react';

interface SteelSection {
  id: number;
  section_name: string;
  section_type: string;
  depth_mm?: number;
  width_mm?: number;
  thickness_mm?: number;
  kg_per_meter: number;
  area_mm2?: number;
  inertia_mm4?: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface SteelElement {
  id: number;
  drawing_id: number;
  element_type: string;
  section_name: string;
  section_type: string;
  length_mm?: number;
  mass_kg?: number;
  confidence_score: number;
  created_at: string;
}

export default function SteelDatabase() {
  const [steelSections, setSteelSections] = useState<SteelSection[]>([]);
  const [steelElements, setSteelElements] = useState<SteelElement[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  useEffect(() => {
    fetchSteelSections();
  }, []);

  const fetchSteelSections = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/steel/sections/');
      if (response.ok) {
        const data = await response.json();
        setSteelSections(data);
      }
    } catch (error) {
      console.error('Error fetching steel sections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      alert('Please select a PDF file');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/api/v1/steel/import-database/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadResult(result);
        setSelectedFile(null);
        fetchSteelSections(); // Refresh the list
        alert('Steel database imported successfully!');
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const searchSections = async () => {
    if (!searchQuery.trim()) {
      fetchSteelSections();
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/steel/sections/search/?query=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const data = await response.json();
        setSteelSections(data);
      }
    } catch (error) {
      console.error('Error searching steel sections:', error);
    }
  };

  const calculateMass = async (sectionName: string, lengthMm: number) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/steel/calculate-mass/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          section_name: sectionName,
          length_mm: lengthMm,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`${sectionName} at ${lengthMm}mm = ${result.mass_kg.toFixed(2)} kg`);
      } else {
        alert('Failed to calculate mass');
      }
    } catch (error) {
      console.error('Error calculating mass:', error);
      alert('Failed to calculate mass');
    }
  };

  return (
    <>
      <Head>
        <title>Steel Database - Construction AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => window.history.back()}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-600" />
                </button>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">Steel Database</h1>
                  <p className="text-sm text-gray-500">Manage steel sections and detect elements</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Database className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-gray-900">
                  {steelSections.length} Sections
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Import British Steel Database</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Upload British Steel UK Sections Database</h3>
              <p className="text-sm text-gray-500 mb-4">
                Upload the British Steel UK sections datasheet PDF to import Universal Beams (UB), Universal Columns (UC), and Unequal Angles (UA)
              </p>
              <div className="flex items-center justify-center space-x-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Select British Steel PDF
                  </span>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
                {selectedFile && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">
                      Selected: {selectedFile.name}
                    </span>
                    <button
                      onClick={handleUpload}
                      disabled={uploading}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50 transition-colors"
                    >
                      {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                  </div>
                )}
              </div>
            </div>
            {uploadResult && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-800">Upload Result</h4>
                <p className="text-sm text-green-700">
                  {uploadResult.message}
                </p>
                <p className="text-sm text-green-700">
                  Sections found: {uploadResult.total_sections_found}, Added: {uploadResult.sections_added}
                </p>
              </div>
            )}
          </div>

          {/* Search Section */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Steel Sections</h2>
            <div className="flex space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search by section name or type..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={searchSections}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <Search className="w-4 h-4" />
                <span>Search</span>
              </button>
            </div>
          </div>

          {/* Steel Sections List */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Steel Sections Database</h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-500 mt-2">Loading steel sections...</p>
              </div>
            ) : steelSections.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No steel sections found</p>
                <p className="text-sm">Upload a steel database PDF to get started</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Section Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        kg/m
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Dimensions
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {steelSections.map((section) => (
                      <tr key={section.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {section.section_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            {section.section_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {section.kg_per_meter} kg/m
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {section.depth_mm && section.width_mm ? 
                            `${section.depth_mm}×${section.width_mm}mm` : 
                            'N/A'
                          }
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => {
                              const length = prompt('Enter length in mm:');
                              if (length) {
                                calculateMass(section.section_name, parseFloat(length));
                              }
                            }}
                            className="text-blue-600 hover:text-blue-900 flex items-center space-x-1"
                          >
                            <Calculator className="w-4 h-4" />
                            <span>Calculate Mass</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
} 
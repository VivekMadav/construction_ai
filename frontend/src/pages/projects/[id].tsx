import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { ArrowLeft, Upload, FileText, Calculator, Download } from 'lucide-react';

interface Project {
  id: number;
  name: string;
  description: string;
  client_name: string;
  project_type: string;
  location: string;
  total_area: number;
  status: string;
  created_at: string;
}

interface Element {
  id: number;
  element_type: string;
  quantity: number;
  unit: string;
  area?: number;
  confidence_score: number;
}

interface Drawing {
  id: number;
  filename: string;
  created_at: string;
  processing_status: string;
  elements?: Element[];
}

export default function ProjectDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [project, setProject] = useState<Project | null>(null);
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedDiscipline, setSelectedDiscipline] = useState<string>("architectural");
  const [selectedDrawing, setSelectedDrawing] = useState<Drawing | null>(null);
  const [showElementsModal, setShowElementsModal] = useState(false);

  useEffect(() => {
    if (id) {
      fetchProject();
      fetchDrawings();
    }
  }, [id]);

  const fetchProject = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/projects/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setProject(data);
      }
    } catch (error) {
      console.error('Error fetching project:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDrawings = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/drawings/project/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setDrawings(data);
      }
    } catch (error) {
      console.error('Error fetching drawings:', error);
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
    formData.append('discipline', selectedDiscipline);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/drawings/upload/${id}/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        alert('Drawing uploaded successfully!');
        setSelectedFile(null);
        fetchDrawings(); // Refresh drawings list
      } else {
        alert('Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const generateCostReport = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/project/${id}/costs/`);
      if (response.ok) {
        const data = await response.json();
        // For demo purposes, show the cost data
        alert(`Cost Analysis Generated!\n\nTotal Cost: £${data.total_cost}\nMaterials: £${data.materials_cost}\nLabor: £${data.labor_cost}\nEquipment: £${data.equipment_cost}\nOverhead: £${data.overhead_cost}`);
      }
    } catch (error) {
      console.error('Error generating cost report:', error);
      alert('Failed to generate cost report');
    }
  };

  const viewElements = (drawing: Drawing) => {
    setSelectedDrawing(drawing);
    setShowElementsModal(true);
  };

  const downloadReport = async (drawing: Drawing) => {
    try {
      // For demo purposes, create a simple report
      const reportContent = `
Construction AI Platform - Drawing Analysis Report

Drawing: ${drawing.filename}
Upload Date: ${drawing.created_at}
Status: ${drawing.processing_status}

Detected Elements:
${drawing.elements?.map(element => 
  `- ${element.element_type}: ${element.quantity} ${element.unit} (Confidence: ${(element.confidence_score * 100).toFixed(0)}%)`
).join('\n') || 'No elements detected'}

Generated on: ${new Date().toLocaleString()}
      `;
      
      // Create and download file
      const blob = new Blob([reportContent], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${drawing.filename.replace('.pdf', '')}_analysis_report.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert('Report downloaded successfully!');
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Failed to download report');
    }
  };

  if (loading) {
    return (
      <>
        <Head>
          <title>Loading Project - Construction AI Platform</title>
        </Head>
        <div className="min-h-screen bg-gray-50 p-8">
          <div className="max-w-6xl mx-auto">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </>
    );
  }

  if (!project) {
    return (
      <>
        <Head>
                      <title>Project Not Found - Construction AI Platform</title>
        </Head>
        <div className="min-h-screen bg-gray-50 p-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">Project Not Found</h1>
              <button
                onClick={() => router.push('/')}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
                    <title>{project.name} - Construction AI Platform</title>
      </Head>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-6xl mx-auto p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/')}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                <p className="text-gray-600">{project.description}</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={generateCostReport}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <Calculator className="w-4 h-4" />
                <span>Generate Cost Report</span>
              </button>
            </div>
          </div>

          {/* Project Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Client</h3>
              <p className="text-lg font-semibold text-gray-900">{project.client_name}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Type</h3>
              <p className="text-lg font-semibold text-gray-900 capitalize">{project.project_type}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Location</h3>
              <p className="text-lg font-semibold text-gray-900">{project.location}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
              <span className={`inline-flex px-2 py-1 text-sm font-medium rounded-full ${
                project.status === 'active' ? 'bg-green-100 text-green-800' :
                project.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {project.status}
              </span>
            </div>
          </div>

          {/* Upload Section */}
          <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Drawing</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
                  <div>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                        Select PDF Drawing
                      </span>
                      <input
                        id="file-upload"
                        type="file"
                        accept=".pdf"
                        onChange={handleFileSelect}
                        className="hidden"
                      />
                    </label>
                  </div>
                  <div>
                    <label htmlFor="discipline-select" className="block text-sm font-medium text-gray-700 mb-1">
                      Drawing Discipline
                    </label>
                    <select
                      id="discipline-select"
                      value={selectedDiscipline}
                      onChange={(e) => setSelectedDiscipline(e.target.value)}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="architectural">Architectural</option>
                      <option value="structural">Structural</option>
                      <option value="civil">Civil</option>
                      <option value="mep">Mechanical/Electrical</option>
                    </select>
                  </div>
                </div>
                {selectedFile && (
                  <div className="text-sm text-gray-600">
                    Selected: {selectedFile.name}
                    <button
                      onClick={handleUpload}
                      disabled={uploading}
                      className="ml-4 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50"
                    >
                      {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                  </div>
                )}
                <p className="text-sm text-gray-500">
                  Upload construction drawings in PDF format for automatic element detection
                </p>
              </div>
            </div>
          </div>

          {/* Drawings List */}
          <div className="bg-white rounded-lg shadow-sm">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Drawings</h2>
            </div>
            {drawings.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No drawings uploaded yet</p>
                <p className="text-sm">Upload a PDF drawing to get started</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {drawings.map((drawing) => (
                  <div key={drawing.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <FileText className="w-8 h-8 text-blue-600" />
                        <div>
                          <h3 className="font-medium text-gray-900">{drawing.filename}</h3>
                          <p className="text-sm text-gray-500">Uploaded: {drawing.created_at}</p>
                          <p className="text-sm text-gray-500">Status: {drawing.processing_status}</p>
                        </div>
                      </div>
                                           <div className="flex space-x-2">
                       <button 
                         onClick={() => viewElements(drawing)}
                         className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                       >
                         View Elements
                       </button>
                       <button 
                         onClick={() => downloadReport(drawing)}
                         className="text-green-600 hover:text-green-800 text-sm font-medium"
                       >
                         <Download className="w-4 h-4 inline mr-1" />
                         Download Report
                       </button>
                     </div>
                    </div>
                    {drawing.elements && drawing.elements.length > 0 && (
                      <div className="mt-4 pl-12">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Detected Elements:</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {drawing.elements.map((element) => (
                            <div key={element.id} className="bg-gray-50 p-3 rounded">
                              <p className="text-sm font-medium capitalize">{element.element_type}</p>
                              <p className="text-xs text-gray-600">
                                {element.quantity} {element.unit}
                              </p>
                              <p className="text-xs text-gray-500">
                                Confidence: {(element.confidence_score * 100).toFixed(0)}%
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Elements Modal */}
      {showElementsModal && selectedDrawing && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detected Elements - {selectedDrawing.filename}
                </h3>
                <button
                  onClick={() => setShowElementsModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {selectedDrawing.elements && selectedDrawing.elements.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {selectedDrawing.elements.map((element) => (
                      <div key={element.id} className="bg-gray-50 p-4 rounded-lg border">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900 capitalize">
                            {element.element_type}
                          </h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            element.confidence_score > 0.8 ? 'bg-green-100 text-green-800' :
                            element.confidence_score > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {(element.confidence_score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                          <p><strong>Quantity:</strong> {element.quantity} {element.unit}</p>
                          {element.area && <p><strong>Area:</strong> {element.area} m²</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Summary</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-blue-600">Total Elements</p>
                        <p className="font-medium">{selectedDrawing.elements.length}</p>
                      </div>
                      <div>
                        <p className="text-blue-600">High Confidence</p>
                        <p className="font-medium">
                          {selectedDrawing.elements.filter(e => e.confidence_score > 0.8).length}
                        </p>
                      </div>
                      <div>
                        <p className="text-blue-600">Medium Confidence</p>
                        <p className="font-medium">
                          {selectedDrawing.elements.filter(e => e.confidence_score > 0.6 && e.confidence_score <= 0.8).length}
                        </p>
                      </div>
                      <div>
                        <p className="text-blue-600">Low Confidence</p>
                        <p className="font-medium">
                          {selectedDrawing.elements.filter(e => e.confidence_score <= 0.6).length}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500">No elements detected yet</p>
                  <p className="text-sm text-gray-400">The drawing is still being processed</p>
                </div>
              )}
              
              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setShowElementsModal(false)}
                  className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
} 
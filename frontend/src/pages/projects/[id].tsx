import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { ArrowLeft, Upload, FileText, Calculator, Download, Building, HardHat, Wrench, Zap } from 'lucide-react';

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

interface SteelElement {
  id: number;
  element_type: string;
  section_name: string;
  section_type: string;
  length_mm?: number;
  mass_kg?: number;
  confidence_score: number;
}

interface ConcreteElement {
  id: number;
  element_type: string;
  concrete_grade: string;
  length_m: number;
  width_m: number;
  depth_m: number;
  volume_m3: number;
  confidence_score: number;
  location?: string;
  description?: string;
}

interface Drawing {
  id: number;
  filename: string;
  created_at: string;
  processing_status: string;
  discipline: string;
  elements?: Element[];
}

interface DisciplineSection {
  name: string;
  key: string;
  icon: React.ReactNode;
  color: string;
  description: string;
}

const DISCIPLINES: DisciplineSection[] = [
  {
    name: "Structural",
    key: "structural",
    icon: <HardHat className="w-6 h-6" />,
    color: "bg-red-50 border-red-200",
    description: "Beams, columns, slabs, foundations, reinforcement details"
  },
  {
    name: "Architectural", 
    key: "architectural",
    icon: <Building className="w-6 h-6" />,
    color: "bg-blue-50 border-blue-200",
    description: "Floor plans, elevations, sections, room layouts"
  },
  {
    name: "Civil",
    key: "civil", 
    icon: <FileText className="w-6 h-6" />,
    color: "bg-green-50 border-green-200",
    description: "Site plans, drainage, roads, landscaping"
  },
  {
    name: "MEP",
    key: "mep",
    icon: <Zap className="w-6 h-6" />,
    color: "bg-purple-50 border-purple-200",
    description: "Mechanical, electrical, plumbing systems"
  }
];

export default function ProjectDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [project, setProject] = useState<Project | null>(null);
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<{ [key: string]: File | null }>({});
  const [selectedDrawing, setSelectedDrawing] = useState<Drawing | null>(null);
  const [showElementsModal, setShowElementsModal] = useState(false);
  const [steelElements, setSteelElements] = useState<SteelElement[]>([]);
  const [loadingSteelElements, setLoadingSteelElements] = useState(false);
  const [concreteElements, setConcreteElements] = useState<ConcreteElement[]>([]);
  const [loadingConcreteElements, setLoadingConcreteElements] = useState(false);

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

  const handleFileSelect = (discipline: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFiles(prev => ({ ...prev, [discipline]: file }));
    } else {
      alert('Please select a PDF file');
    }
  };

  const handleUpload = async (discipline: string) => {
    const file = selectedFiles[discipline];
    if (!file) return;

    setUploading(discipline);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('discipline', discipline);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/drawings/upload/${id}/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setSelectedFiles(prev => ({ ...prev, [discipline]: null }));
        fetchDrawings();
        alert(`${discipline.charAt(0).toUpperCase() + discipline.slice(1)} drawing uploaded successfully!`);
      } else {
        alert('Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(null);
    }
  };

  const generateCostReport = async (drawingId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/drawing/${drawingId}/costs/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cost-report-${drawingId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error generating cost report:', error);
      alert('Failed to generate cost report');
    }
  };

  const viewElements = async (drawing: Drawing) => {
    setSelectedDrawing(drawing);
    setShowElementsModal(true);
    
    // Fetch steel elements for all drawings
    setLoadingSteelElements(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/steel/elements/drawing/${drawing.id}`);
      if (response.ok) {
        const data = await response.json();
        setSteelElements(data.elements || data);
      }
    } catch (error) {
      console.error('Error fetching steel elements:', error);
    } finally {
      setLoadingSteelElements(false);
    }
    
    // Fetch concrete elements for all drawings
    setLoadingConcreteElements(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/concrete/elements/drawing/${drawing.id}`);
      if (response.ok) {
        const data = await response.json();
        setConcreteElements(data.elements || []);
      }
    } catch (error) {
      console.error('Error fetching concrete elements:', error);
    } finally {
      setLoadingConcreteElements(false);
    }
  };

  const downloadReport = async (drawing: Drawing) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/drawing/${drawing.id}/report/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `drawing-report-${drawing.id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Failed to download report');
    }
  };

  const deleteDrawing = async (drawing: Drawing) => {
    const message = drawing.processing_status === 'failed' 
      ? `Remove failed upload "${drawing.filename}"? This will delete the file permanently.`
      : `Are you sure you want to delete "${drawing.filename}"? This action cannot be undone.`;
    
    if (!confirm(message)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/drawings/${drawing.id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const successMessage = drawing.processing_status === 'failed' 
          ? 'Failed upload removed successfully'
          : 'Drawing deleted successfully';
        alert(successMessage);
        // Refresh the drawings list
        fetchDrawings();
      } else {
        const errorData = await response.json();
        alert(`Failed to delete drawing: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting drawing:', error);
      alert('Failed to delete drawing');
    }
  };

  const retryDrawing = async (drawing: Drawing) => {
    if (!confirm(`Retry processing "${drawing.filename}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/drawings/${drawing.id}/reprocess`, {
        method: 'POST'
      });
      
      if (response.ok) {
        alert('Drawing reprocessing started. Please wait a moment and refresh the page.');
        // Refresh the drawings list after a short delay
        setTimeout(() => {
          fetchDrawings();
        }, 2000);
      } else {
        const errorData = await response.json();
        alert(`Failed to retry processing: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error retrying drawing:', error);
      alert('Failed to retry processing');
    }
  };



  const getDrawingsByDiscipline = (discipline: string) => {
    return drawings.filter(drawing => drawing.discipline === discipline);
  };

  const getDisciplineStats = (discipline: string) => {
    const disciplineDrawings = getDrawingsByDiscipline(discipline);
    const totalElements = disciplineDrawings.reduce((sum, drawing) => 
      sum + (drawing.elements?.length || 0), 0);
    const completedDrawings = disciplineDrawings.filter(d => d.processing_status === 'completed').length;
    
    return {
      totalDrawings: disciplineDrawings.length,
      completedDrawings,
      totalElements,
      pendingDrawings: disciplineDrawings.filter(d => d.processing_status === 'pending').length,
      failedDrawings: disciplineDrawings.filter(d => d.processing_status === 'failed').length
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Project not found</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{project.name} - Construction AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => router.push('/')}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-600" />
                </button>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">{project.name}</h1>
                  <p className="text-sm text-gray-500">{project.client_name} • {project.project_type}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  project.status === 'active' ? 'bg-green-100 text-green-800' :
                  project.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {project.status}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Project Overview */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Location</p>
                <p className="font-medium">{project.location || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Area</p>
                <p className="font-medium">{project.total_area ? `${project.total_area} m²` : 'Not specified'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created</p>
                <p className="font-medium">{new Date(project.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            {project.description && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Description</p>
                <p className="text-gray-700">{project.description}</p>
              </div>
            )}
          </div>

          {/* Discipline Sections */}
          <div className="space-y-8">
            {DISCIPLINES.map((discipline) => {
              const stats = getDisciplineStats(discipline.key);
              const disciplineDrawings = getDrawingsByDiscipline(discipline.key);
              
              return (
                <div key={discipline.key} className={`border rounded-lg ${discipline.color}`}>
                  {/* Discipline Header */}
                  <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-white rounded-lg shadow-sm">
                          {discipline.icon}
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{discipline.name} Drawings</h3>
                          <p className="text-sm text-gray-600">{discipline.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 text-sm">
                        <div className="text-center">
                          <p className="font-semibold text-gray-900">{stats.totalDrawings}</p>
                          <p className="text-gray-500">Drawings</p>
                        </div>
                        <div className="text-center">
                          <p className="font-semibold text-gray-900">{stats.totalElements}</p>
                          <p className="text-gray-500">Elements</p>
                        </div>
                        <div className="text-center">
                          <p className="font-semibold text-green-600">{stats.completedDrawings}</p>
                          <p className="text-gray-500">Completed</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Upload Section */}
                  <div className="p-6 border-b border-gray-200">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h4 className="text-lg font-medium text-gray-900 mb-2">Upload {discipline.name} Drawing</h4>
                      <p className="text-sm text-gray-500 mb-4">
                        Upload construction drawings in PDF format for automatic element detection
                      </p>
                      <div className="flex items-center justify-center space-x-4">
                        <label htmlFor={`file-upload-${discipline.key}`} className="cursor-pointer">
                          <span className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                            Select PDF Drawing
                          </span>
                          <input
                            id={`file-upload-${discipline.key}`}
                            type="file"
                            accept=".pdf"
                            onChange={(e) => handleFileSelect(discipline.key, e)}
                            className="hidden"
                          />
                        </label>
                        {selectedFiles[discipline.key] && (
                          <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-600">
                              Selected: {selectedFiles[discipline.key]?.name}
                            </span>
                            <button
                              onClick={() => handleUpload(discipline.key)}
                              disabled={uploading === discipline.key}
                              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50 transition-colors"
                            >
                              {uploading === discipline.key ? 'Uploading...' : 'Upload'}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Drawings List */}
                  <div className="p-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-4">Uploaded Drawings</h4>
                    {disciplineDrawings.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p>No {discipline.name.toLowerCase()} drawings uploaded yet</p>
                        <p className="text-sm">Upload your first drawing to get started</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {disciplineDrawings.map((drawing) => (
                          <div key={drawing.id} className="bg-white rounded-lg border p-4 flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <FileText className="w-5 h-5 text-gray-400" />
                              <div>
                                <p className="font-medium text-gray-900">{drawing.filename}</p>
                                <p className="text-sm text-gray-500">
                                  Uploaded {new Date(drawing.created_at).toLocaleDateString()}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                drawing.processing_status === 'completed' ? 'bg-green-100 text-green-800' :
                                drawing.processing_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                                drawing.processing_status === 'failed' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {drawing.processing_status}
                              </span>
                              {drawing.processing_status === 'completed' && (
                                <>
                                  <button
                                    onClick={() => viewElements(drawing)}
                                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                                  >
                                    View Elements
                                  </button>
                                  <button
                                    onClick={() => generateCostReport(drawing.id)}
                                    className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                                  >
                                    Cost Report
                                  </button>
                                  <button
                                    onClick={() => downloadReport(drawing)}
                                    className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700 transition-colors"
                                  >
                                    Download Report
                                  </button>
                                  <button
                                    onClick={() => deleteDrawing(drawing)}
                                    className="text-gray-500 hover:text-red-600 transition-colors p-1"
                                    title="Delete drawing"
                                  >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                      <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                    </svg>
                                  </button>
                                </>
                              )}
                              {drawing.processing_status === 'failed' && (
                                <>
                                  <button
                                    onClick={() => retryDrawing(drawing)}
                                    className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700 transition-colors"
                                    title="Retry processing"
                                  >
                                    Retry
                                  </button>
                                  <button
                                    onClick={() => deleteDrawing(drawing)}
                                    className="text-red-500 hover:text-red-700 transition-colors p-1"
                                    title="Remove failed upload"
                                  >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                      <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                    </svg>
                                  </button>
                                </>
                              )}
                              {drawing.processing_status === 'processing' && (
                                <div className="flex items-center space-x-2">
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                  <span className="text-sm text-gray-500">Processing...</span>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Elements Modal */}
        {showElementsModal && selectedDrawing && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Elements in {selectedDrawing.filename}
                  </h3>
                  <button
                    onClick={() => setShowElementsModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>


                {/* Steel Elements Section */}
                <div className="mb-6">
                  <h4 className="text-md font-medium text-gray-900 mb-3">Steel Elements</h4>
                  {loadingSteelElements ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="mt-2 text-gray-500">Loading steel elements...</p>
                    </div>
                  ) : steelElements.length > 0 ? (
                    <div className="space-y-3">
                      {steelElements.map((element, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <div>
                            <p className="font-medium text-gray-900">{element.element_type}</p>
                            <p className="text-sm text-gray-500">
                              {element.section_name} ({element.section_type})
                              {element.length_mm && ` • ${element.length_mm}mm`}
                              {element.mass_kg && ` • ${element.mass_kg.toFixed(2)} kg`}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">
                              {Math.round(element.confidence_score * 100)}%
                            </p>
                            <p className="text-xs text-gray-500">Confidence</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No steel elements detected in this drawing.</p>
                  )}
                </div>

                {/* Concrete Elements Section */}
                <div className="mb-6">
                  <h4 className="text-md font-medium text-gray-900 mb-3">Concrete Elements</h4>
                  {loadingConcreteElements ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-600 mx-auto"></div>
                      <p className="mt-2 text-gray-500">Loading concrete elements...</p>
                    </div>
                  ) : concreteElements.length > 0 ? (
                    <div className="space-y-3">
                      {concreteElements.map((element, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                          <div>
                            <p className="font-medium text-gray-900">{element.element_type}</p>
                            <p className="text-sm text-gray-500">
                              {element.concrete_grade} • {element.volume_m3.toFixed(2)} m³
                              <br />
                              {element.length_m.toFixed(2)}m × {element.width_m.toFixed(2)}m × {element.depth_m.toFixed(2)}m
                              {element.location && ` • ${element.location}`}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">
                              {Math.round(element.confidence_score * 100)}%
                            </p>
                            <p className="text-xs text-gray-500">Confidence</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No concrete elements detected in this drawing.</p>
                  )}
                </div>

                {steelElements.length === 0 && concreteElements.length === 0 && (
                  <p className="text-gray-500">No steel or concrete elements detected in this drawing.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
} 
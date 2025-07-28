import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useQuery } from 'react-query';
import axios from 'axios';
import { 
  PlusIcon, 
  DocumentTextIcon, 
  CalculatorIcon, 
  ChartBarIcon,
  CloudArrowUpIcon,
  MagnifyingGlassIcon as Search,
  FunnelIcon as Filter,
  PencilIcon as Edit,
  TrashIcon as Trash2,
  EyeIcon as Eye,
  ArrowDownTrayIcon as Download,
  CircleStackIcon as Database 
} from '@heroicons/react/24/outline';

interface Project {
  id: number;
  name: string;
  description: string;
  status: string;
  total_cost: number;
  created_at: string;
  client_name: string;
  project_type?: string;
  location?: string;
}

interface DashboardStats {
  totalProjects: number;
  activeProjects: number;
  totalValue: number;
  drawingsProcessed: number;
}

export default function Dashboard() {
  const router = useRouter();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    client_name: '',
    project_type: '',
    location: '',
    status: 'draft'
  });

  const { data: projects, isLoading, refetch } = useQuery<Project[]>(
    'projects',
    async () => {
      const response = await axios.get('/api/v1/projects/');
      return response.data;
    },
    {
      refetchOnWindowFocus: false,
      refetchInterval: 5000, // Refetch every 5 seconds for live updates
    }
  );

  // Fetch dashboard statistics
  const { data: dashboardStats } = useQuery<DashboardStats>(
    'dashboardStats',
    async () => {
      const [projectsResponse, drawingsResponse, costResponse] = await Promise.all([
        axios.get('/api/v1/projects/'),
        axios.get('/api/v1/drawings/'),
        axios.get('/api/v1/analysis/costs')
      ]);

      const projects = projectsResponse.data;
      const drawings = drawingsResponse.data;
      const costAnalysis = costResponse.data;

      return {
        totalProjects: projects.length,
        activeProjects: projects.filter((p: Project) => p.status === 'active').length,
        totalValue: costAnalysis.total_cost || 0,
        drawingsProcessed: drawings.filter((d: any) => d.processing_status === 'completed').length
      };
    },
    {
      refetchOnWindowFocus: false,
      refetchInterval: 5000, // Refetch every 5 seconds for live updates
    }
  );

  // Fetch individual project costs
  const { data: projectCosts } = useQuery<Record<number, number>>(
    'projectCosts',
    async () => {
      if (!projects) return {};
      
      const costPromises = projects.map(async (project) => {
        try {
          const response = await axios.get(`/api/v1/analysis/project/${project.id}/costs`);
          return { id: project.id, cost: response.data.total_cost || 0 };
        } catch (error) {
          console.error(`Error fetching cost for project ${project.id}:`, error);
          return { id: project.id, cost: 0 };
        }
      });

      const costs = await Promise.all(costPromises);
      return costs.reduce((acc, { id, cost }) => {
        acc[id] = cost;
        return acc;
      }, {} as Record<number, number>);
    },
    {
      refetchOnWindowFocus: false,
      refetchInterval: 5000, // Refetch every 5 seconds for live updates
      enabled: !!projects,
    }
  );

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Creating project with data:', newProject);
    try {
      const response = await axios.post('/api/v1/projects/', newProject);
      console.log('Project created successfully:', response.data);
      setIsCreateModalOpen(false);
      setNewProject({ name: '', description: '', client_name: '', project_type: '', location: '', status: 'draft' });
      refetch();
    } catch (error) {
      console.error('Error creating project:', error);
      if (axios.isAxiosError(error)) {
        console.error('Response data:', error.response?.data);
        console.error('Response status:', error.response?.status);
      }
    }
  };

  const handleEditProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProject) return;
    
    try {
      await axios.put(`/api/v1/projects/${editingProject.id}/`, {
        name: editingProject.name,
        description: editingProject.description,
        client_name: editingProject.client_name,
        project_type: editingProject.project_type,
        location: editingProject.location,
        status: editingProject.status
      });
      setIsEditModalOpen(false);
      setEditingProject(null);
      refetch();
    } catch (error) {
      console.error('Error updating project:', error);
    }
  };

  const openEditModal = (project: Project) => {
    setEditingProject(project);
    setIsEditModalOpen(true);
  };

  return (
    <>
      <Head>
        <title>Construction AI Platform - Dashboard</title>
        <meta name="description" content="AI-powered quantity surveying platform" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Construction AI Platform</h1>
                <p className="text-gray-600">AI-powered construction cost estimation</p>
              </div>
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="btn-primary flex items-center gap-2"
              >
                <PlusIcon className="h-5 w-5" />
                New Project
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-3"
            >
                              <PlusIcon className="w-6 h-6" />
              <div className="text-left">
                <div className="font-semibold">Create Project</div>
                <div className="text-sm opacity-90">Start a new construction project</div>
              </div>
            </button>
            
            <a
              href="/steel-database"
              className="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-3"
            >
              <Database className="w-6 h-6" />
              <div className="text-left">
                <div className="font-semibold">Steel Database</div>
                <div className="text-sm opacity-90">Manage steel sections and detection</div>
              </div>
            </a>
            
            <div className="bg-purple-600 text-white p-4 rounded-lg flex items-center space-x-3">
              <Download className="w-6 h-6" />
              <div className="text-left">
                <div className="font-semibold">Export Data</div>
                <div className="text-sm opacity-90">Download reports and analysis</div>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center">
                <DocumentTextIcon className="h-8 w-8 text-primary-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Projects</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardStats?.totalProjects || 0}</p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center">
                <CalculatorIcon className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Projects</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardStats?.activeProjects || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Value</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${dashboardStats?.totalValue?.toLocaleString() || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center">
                <CloudArrowUpIcon className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Drawings Processed</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardStats?.drawingsProcessed || 0}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Projects List */}
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Recent Projects</h2>
            </div>
            
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading projects...</p>
              </div>
            ) : projects && projects.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Project Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Client
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total Cost
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {projects.map((project) => (
                      <tr 
                        key={project.id} 
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => router.push(`/projects/${project.id}`)}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{project.name}</div>
                            <div className="text-sm text-gray-500">{project.description}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {project.client_name || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <select
                            value={project.status}
                            onChange={async (e) => {
                              try {
                                await axios.put(`/api/v1/projects/${project.id}`, {
                                  status: e.target.value
                                });
                                refetch(); // Refresh the data
                              } catch (error) {
                                console.error('Error updating project status:', error);
                              }
                            }}
                            className={`text-xs font-semibold rounded px-2 py-1 border-0 ${
                              project.status === 'active' 
                                ? 'bg-green-100 text-green-800'
                                : project.status === 'completed'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                            onClick={(e) => e.stopPropagation()} // Prevent row click
                          >
                            <option value="draft">draft</option>
                            <option value="active">active</option>
                            <option value="completed">completed</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${projectCosts?.[project.id]?.toLocaleString() || '0'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(project.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              openEditModal(project);
                            }}
                            className="text-blue-600 hover:text-blue-900 font-medium"
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
                <div className="mt-6">
                  <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="btn-primary"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    New Project
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Create Project Modal */}
        {isCreateModalOpen && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Project</h3>
                <form onSubmit={handleCreateProject}>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Project Name</label>
                      <input
                        type="text"
                        required
                        className="input-field mt-1"
                        value={newProject.name}
                        onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        className="input-field mt-1"
                        rows={3}
                        value={newProject.description}
                        onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Client Name</label>
                      <input
                        type="text"
                        className="input-field mt-1"
                        value={newProject.client_name}
                        onChange={(e) => setNewProject({...newProject, client_name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Project Type</label>
                      <select
                        className="input-field mt-1"
                        value={newProject.project_type}
                        onChange={(e) => setNewProject({...newProject, project_type: e.target.value})}
                      >
                        <option value="">Select type</option>
                        <option value="residential">Residential</option>
                        <option value="commercial">Commercial</option>
                        <option value="industrial">Industrial</option>
                        <option value="infrastructure">Infrastructure</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Location</label>
                      <input
                        type="text"
                        className="input-field mt-1"
                        value={newProject.location}
                        onChange={(e) => setNewProject({...newProject, location: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Status</label>
                      <select
                        className="input-field mt-1"
                        value={newProject.status}
                        onChange={(e) => setNewProject({...newProject, status: e.target.value})}
                      >
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end space-x-3 mt-6">
                    <button
                      type="button"
                      onClick={() => setIsCreateModalOpen(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      Create Project
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Edit Project Modal */}
        {isEditModalOpen && editingProject && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Project</h3>
                <form onSubmit={handleEditProject}>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Project Name</label>
                      <input
                        type="text"
                        required
                        className="input-field mt-1"
                        value={editingProject.name}
                        onChange={(e) => setEditingProject({...editingProject, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        className="input-field mt-1"
                        rows={3}
                        value={editingProject.description || ''}
                        onChange={(e) => setEditingProject({...editingProject, description: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Client Name</label>
                      <input
                        type="text"
                        className="input-field mt-1"
                        value={editingProject.client_name || ''}
                        onChange={(e) => setEditingProject({...editingProject, client_name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Project Type</label>
                      <select
                        className="input-field mt-1"
                        value={editingProject.project_type || ''}
                        onChange={(e) => setEditingProject({...editingProject, project_type: e.target.value})}
                      >
                        <option value="">Select type</option>
                        <option value="residential">Residential</option>
                        <option value="commercial">Commercial</option>
                        <option value="industrial">Industrial</option>
                        <option value="infrastructure">Infrastructure</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Location</label>
                      <input
                        type="text"
                        className="input-field mt-1"
                        value={editingProject.location || ''}
                        onChange={(e) => setEditingProject({...editingProject, location: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Status</label>
                      <select
                        className="input-field mt-1"
                        value={editingProject.status}
                        onChange={(e) => setEditingProject({...editingProject, status: e.target.value})}
                      >
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end space-x-3 mt-6">
                    <button
                      type="button"
                      onClick={() => {
                        setIsEditModalOpen(false);
                        setEditingProject(null);
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      Update Project
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
} 
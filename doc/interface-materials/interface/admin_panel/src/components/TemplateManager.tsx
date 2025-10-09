import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import {
  FileText,
  Upload,
  Download,
  Eye,
  Edit3,
  Trash2,
  Search,
  Filter,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  ExternalLink,
  FileUp,
  Clock,
  User,
  Tag
} from 'lucide-react';
import { templateService, Template, TemplateCategory } from '@/services/templates';

const TemplateManager: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    name: '',
    category: 'form' as Template['category'],
    description: '',
    version: '1.0',
    tags: ''
  });

  useEffect(() => {
    loadTemplates();
    loadCategories();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      console.log('📄 Loading templates from all sources...');
      const templatesData = await templateService.getAdminTemplates();
      setTemplates(templatesData);
      console.log('✅ Templates loaded:', templatesData.length);
    } catch (error) {
      console.error('❌ Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const categoriesData = await templateService.getTemplateCategories();
      const categoriesWithCounts = categoriesData.map(cat => ({
        ...cat,
        template_count: templates.filter(t => t.category === cat.id).length
      }));
      setCategories(categoriesWithCounts);
    } catch (error) {
      console.error('❌ Failed to load categories:', error);
    }
  };

  const handleUpload = async (file: File) => {
    if (!file) return;

    setUploading(true);
    try {
      const metadata = {
        name: uploadForm.name || file.name,
        category: uploadForm.category,
        description: uploadForm.description,
        version: uploadForm.version,
        tags: uploadForm.tags.split(',').map(tag => tag.trim()).filter(Boolean)
      };

      console.log('📤 Starting template upload process...');
      const success = await templateService.uploadTemplate(file, metadata);

      if (success) {
        console.log('✅ Template uploaded successfully');
        await loadTemplates();
        setUploadDialogOpen(false);
        setUploadForm({
          name: '',
          category: 'form',
          description: '',
          version: '1.0',
          tags: ''
        });
      } else {
        console.error('❌ Template upload failed');
      }
    } catch (error) {
      console.error('❌ Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const filteredTemplates = templates.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const renderTemplateCard = (template: Template) => (
    <Card key={template.id} className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              {template.name}
            </CardTitle>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline">{template.category}</Badge>
              <Badge
                variant={template.status === 'active' ? 'default' : template.status === 'draft' ? 'secondary' : 'destructive'}
              >
                {template.status}
              </Badge>
              <Badge variant="outline" className="text-xs">
                v{template.version}
              </Badge>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="ghost">
              <Eye className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost">
              <Download className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost">
              <Edit3 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground mb-3">{template.description}</p>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-muted-foreground" />
            <span>{template.created_by}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{new Date(template.created_date).toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span>{template.file_type.toUpperCase()}</span>
          </div>
          <div className="flex items-center gap-2">
            <Eye className="h-4 w-4 text-muted-foreground" />
            <span>{template.usage_count} uses</span>
          </div>
        </div>

        {template.tags.length > 0 && (
          <div className="flex items-center gap-1 mt-3">
            <Tag className="h-4 w-4 text-muted-foreground" />
            <div className="flex flex-wrap gap-1">
              {template.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading templates from all sources...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">BCM Template Management</h3>
          <p className="text-sm text-muted-foreground">
            Manage templates from Odoo, Document Processor, and File System
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload Template
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Upload New Template</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Template Name</Label>
                  <Input
                    value={uploadForm.name}
                    onChange={(e) => setUploadForm(prev => ({...prev, name: e.target.value}))}
                    placeholder="Enter template name"
                  />
                </div>
                <div>
                  <Label>Category</Label>
                  <Select
                    value={uploadForm.category}
                    onValueChange={(value: Template['category']) => setUploadForm(prev => ({...prev, category: value}))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="policy">Policy</SelectItem>
                      <SelectItem value="procedure">Procedure</SelectItem>
                      <SelectItem value="plan">Plan</SelectItem>
                      <SelectItem value="assessment">Assessment</SelectItem>
                      <SelectItem value="report">Report</SelectItem>
                      <SelectItem value="form">Form</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm(prev => ({...prev, description: e.target.value}))}
                    placeholder="Template description"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Version</Label>
                    <Input
                      value={uploadForm.version}
                      onChange={(e) => setUploadForm(prev => ({...prev, version: e.target.value}))}
                      placeholder="1.0"
                    />
                  </div>
                  <div>
                    <Label>Tags (comma-separated)</Label>
                    <Input
                      value={uploadForm.tags}
                      onChange={(e) => setUploadForm(prev => ({...prev, tags: e.target.value}))}
                      placeholder="iso22301, bcm"
                    />
                  </div>
                </div>
                <div>
                  <Label>File</Label>
                  <Input
                    type="file"
                    accept=".docx,.pdf,.xlsx,.html"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleUpload(file);
                    }}
                    disabled={uploading}
                  />
                </div>
                {uploading && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Processing through Document Processor and saving to Odoo...
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>

          <Button variant="outline" onClick={loadTemplates}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search templates by name, description, or tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-48">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map(cat => (
              <SelectItem key={cat.id} value={cat.id}>
                {cat.name} ({cat.template_count})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Templates Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredTemplates.map(renderTemplateCard)}
      </div>

      {filteredTemplates.length === 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            No templates found matching your criteria. Try adjusting the search or category filter.
          </AlertDescription>
        </Alert>
      )}

      {/* Integration Status */}
      <Alert>
        <CheckCircle className="h-4 w-4" />
        <AlertTitle>Multi-Source Template Integration</AlertTitle>
        <AlertDescription>
          Templates are loaded from Odoo (bcm_document), Document Processor (localhost:8083), and File System.
          Uploads are processed through AI and stored across all systems for maximum availability.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default TemplateManager;
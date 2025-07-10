
import React, { useState, useCallback } from 'react';
import { Upload, Image, AlertCircle, CheckCircle, Loader2, Camera, Shield, Search, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import TransactionAnalysisResults from '@/components/TransactionAnalysisResults';

interface AnalysisResult {
  result: 'Original' | 'Edited';
  confidence: number;
  details?: string;
  processing_time?: number;
  analysis_type?: string;
  transaction_analysis?: any;
  reverse_search?: any;
  tampered_regions?: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    confidence: number;
  }>;
}

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [transactionMode, setTransactionMode] = useState(true);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelection = (file: File) => {
    if (!file.type.match(/^image\/(png|jpeg|jpg)$/i)) {
      setError('Please select a PNG or JPEG image file.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB.');
      return;
    }

    setError(null);
    setSelectedFile(file);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const analyzeImage = async () => {
    if (!selectedFile) return;

    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('transaction_mode', transactionMode.toString());

    try {
      console.log('Sending request to backend with transaction_mode:', transactionMode);
      
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Analysis failed: ${response.statusText} - ${errorText}`);
      }

      // Get the response as text first to check if it's valid JSON
      const responseText = await response.text();
      console.log('Raw response:', responseText.substring(0, 500) + '...');

      if (!responseText.trim()) {
        throw new Error('Empty response from server');
      }

      let analysisResult: AnalysisResult;
      try {
        analysisResult = JSON.parse(responseText);
      } catch (jsonError) {
        console.error('JSON parsing error:', jsonError);
        console.error('Response text:', responseText);
        throw new Error('Invalid JSON response from server. The analysis may have timed out or encountered an error.');
      }

      console.log('Parsed analysis result:', analysisResult);
      setResult(analysisResult);
    } catch (err) {
      console.error('Analysis error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed. Please try again.';
      setError(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const getResultColor = (result: string) => {
    return result === 'Original' ? 'text-green-600' : 'text-red-600';
  };

  const getResultBadgeVariant = (result: string) => {
    return result === 'Original' ? 'default' : 'destructive';
  };

  const getRiskLevel = () => {
    if (!result?.transaction_analysis) return null;
    
    const highRisk = result.transaction_analysis.fraud_indicators?.filter((i: any) => i.severity === 'high').length || 0;
    const mediumRisk = result.transaction_analysis.fraud_indicators?.filter((i: any) => i.severity === 'medium').length || 0;
    
    if (highRisk > 0) return { level: 'HIGH', color: 'text-red-600', bgColor: 'bg-red-50' };
    if (mediumRisk > 2) return { level: 'MEDIUM', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { level: 'LOW', color: 'text-green-600', bgColor: 'bg-green-50' };
  };

  const riskLevel = getRiskLevel();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-3">
            <Shield className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">ScreenGuard</h1>
            <Badge variant="outline" className="ml-2">Enhanced</Badge>
          </div>
          <p className="text-gray-600 mt-1">AI-powered image authenticity & transaction fraud detection</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Camera className="h-5 w-5" />
                <span>Upload Image</span>
              </CardTitle>
              <CardDescription>
                Upload a screenshot or transaction image for comprehensive fraud analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Transaction Mode Toggle */}
              <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
                <Switch
                  id="transaction-mode"
                  checked={transactionMode}
                  onCheckedChange={setTransactionMode}
                />
                <Label htmlFor="transaction-mode" className="text-sm">
                  Enable transaction fraud detection (metadata, reverse search, pattern analysis)
                </Label>
              </div>

              {!preview ? (
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
                    dragActive
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-gray-900">
                      Drop your image here
                    </p>
                    <p className="text-gray-500">or click to browse</p>
                    <p className="text-sm text-gray-400">
                      Supports PNG, JPEG (max 10MB)
                    </p>
                  </div>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={handleFileInputChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative">
                    <img
                      src={preview}
                      alt="Upload preview"
                      className="w-full h-64 object-contain bg-gray-50 rounded-lg border"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">{selectedFile?.name}</p>
                      <p>{selectedFile && (selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <Button variant="outline" onClick={resetUpload} size="sm">
                      Remove
                    </Button>
                  </div>
                </div>
              )}

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                onClick={analyzeImage}
                disabled={!selectedFile || analyzing}
                className="w-full"
                size="lg"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {transactionMode ? 'Running Comprehensive Analysis...' : 'Analyzing Image...'}
                  </>
                ) : (
                  <>
                    <Image className="mr-2 h-4 w-4" />
                    {transactionMode ? 'Analyze for Fraud' : 'Basic Analysis'}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Results Section */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Analysis Results</span>
              </CardTitle>
              <CardDescription>
                {transactionMode ? 'Comprehensive fraud detection results' : 'Basic authenticity analysis'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analyzing && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                    <span className="text-sm text-gray-600">
                      {transactionMode ? 'Running comprehensive analysis...' : 'Processing image...'}
                    </span>
                  </div>
                  <Progress value={65} className="w-full" />
                  <p className="text-xs text-gray-500">
                    {transactionMode 
                      ? 'Analyzing metadata, performing reverse search, detecting patterns...'
                      : 'Running deep learning analysis using advanced tampering detection models'
                    }
                  </p>
                </div>
              )}

              {result && !analyzing && (
                <div className="space-y-6">
                  <div className="text-center space-y-4">
                    <div className="flex items-center justify-center space-x-2">
                      {result.result === 'Original' ? (
                        <CheckCircle className="h-8 w-8 text-green-600" />
                      ) : (
                        <AlertCircle className="h-8 w-8 text-red-600" />
                      )}
                      <h3 className={`text-2xl font-bold ${getResultColor(result.result)}`}>
                        {result.result}
                      </h3>
                    </div>
                    
                    <div className="flex items-center justify-center space-x-2">
                      <Badge variant={getResultBadgeVariant(result.result)} className="text-sm px-3 py-1">
                        {(result.confidence * 100).toFixed(1)}% Confidence
                      </Badge>
                      {result.analysis_type === 'comprehensive' && (
                        <Badge variant="outline" className="text-sm px-3 py-1">
                          Comprehensive
                        </Badge>
                      )}
                    </div>

                    {/* Risk Level for Transaction Analysis */}
                    {riskLevel && (
                      <div className={`p-3 rounded-lg ${riskLevel.bgColor}`}>
                        <div className="flex items-center justify-center space-x-2">
                          <AlertTriangle className={`h-5 w-5 ${riskLevel.color}`} />
                          <span className={`font-bold ${riskLevel.color}`}>
                            {riskLevel.level} RISK TRANSACTION
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Confidence Score</span>
                      <span className="text-sm text-gray-600">
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={result.confidence * 100} className="w-full" />
                  </div>

                  {result.details && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Analysis Details</h4>
                      <p className="text-sm text-gray-600">{result.details}</p>
                    </div>
                  )}

                  {result.processing_time && (
                    <div className="text-xs text-gray-500 text-center">
                      Analysis completed in {result.processing_time.toFixed(2)}s
                    </div>
                  )}
                </div>
              )}

              {!analyzing && !result && (
                <div className="text-center py-12 text-gray-500">
                  <Image className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                  <p className="text-lg font-medium">Ready for Analysis</p>
                  <p className="text-sm">
                    {transactionMode 
                      ? 'Upload a transaction screenshot for fraud detection'
                      : 'Upload an image to get started'
                    }
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Detailed Transaction Analysis Results */}
        {result?.transaction_analysis && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Detailed Fraud Analysis</h2>
            <TransactionAnalysisResults 
              transactionAnalysis={result.transaction_analysis}
              reverseSearch={result.reverse_search}
            />
          </div>
        )}

        {/* Enhanced Info Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 mb-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold">AI Detection</h3>
              </div>
              <p className="text-sm text-gray-600">
                Advanced models analyze pixel patterns and detect digital tampering.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 mb-2">
                <Search className="h-5 w-5 text-purple-600" />
                <h3 className="font-semibold">Reverse Search</h3>
              </div>
              <p className="text-sm text-gray-600">
                Check if images exist online to verify originality and detect reuse.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <h3 className="font-semibold">Fraud Detection</h3>
              </div>
              <p className="text-sm text-gray-600">
                Specialized analysis for transaction screenshots and financial fraud.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 mb-2">
                <Camera className="h-5 w-5 text-green-600" />
                <h3 className="font-semibold">Privacy First</h3>
              </div>
              <p className="text-sm text-gray-600">
                All analysis performed securely. Images processed only for detection.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Index;
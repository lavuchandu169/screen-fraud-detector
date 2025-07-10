
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle, Info, MapPin, Calendar, DollarSign, Eye, Search, Shield } from 'lucide-react';

interface FraudIndicator {
  type: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  location: string;
}

interface SuspiciousRegion {
  type: string;
  location?: { x: number; y: number };
  size?: { width: number; height: number };
  confidence?: number;
  description: string;
  severity?: string;
}

interface TransactionAnalysis {
  metadata_analysis: {
    has_exif: boolean;
    creation_date?: string;
    device_info?: string;
    software_used?: string;
    suspicious_metadata: string[];
  };
  text_analysis: {
    extracted_text: string;
    detected_amounts: string[];
    detected_dates: string[];
    app_identified?: string;
    text_anomalies: string[];
  };
  fraud_indicators: FraudIndicator[];
  recommendations: string[];
  suspicious_regions: SuspiciousRegion[];
}

interface ReverseSearch {
  found_matches: boolean;
  similar_images: number;
  earliest_occurrence?: string;
  warnings: string[];
}

interface TransactionAnalysisResultsProps {
  transactionAnalysis: TransactionAnalysis;
  reverseSearch?: ReverseSearch;
}

const TransactionAnalysisResults: React.FC<TransactionAnalysisResultsProps> = ({
  transactionAnalysis,
  reverseSearch
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high': return <Badge variant="destructive">High Risk</Badge>;
      case 'medium': return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Medium Risk</Badge>;
      case 'low': return <Badge variant="outline">Low Risk</Badge>;
      default: return <Badge variant="outline">Info</Badge>;
    }
  };

  const highRiskIndicators = transactionAnalysis.fraud_indicators.filter(i => i.severity === 'high');
  const mediumRiskIndicators = transactionAnalysis.fraud_indicators.filter(i => i.severity === 'medium');

  return (
    <div className="space-y-6">
      {/* Risk Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Risk Assessment</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-lg bg-red-50 border border-red-200">
              <div className="text-2xl font-bold text-red-600">{highRiskIndicators.length}</div>
              <div className="text-sm text-red-600">High Risk Issues</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-yellow-50 border border-yellow-200">
              <div className="text-2xl font-bold text-yellow-600">{mediumRiskIndicators.length}</div>
              <div className="text-sm text-yellow-600">Medium Risk Issues</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
              <div className="text-2xl font-bold text-blue-600">{transactionAnalysis.suspicious_regions.length}</div>
              <div className="text-sm text-blue-600">Suspicious Regions</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Fraud Indicators */}
      {transactionAnalysis.fraud_indicators.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span>Fraud Indicators</span>
            </CardTitle>
            <CardDescription>
              Suspicious patterns detected in the image analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {transactionAnalysis.fraud_indicators.map((indicator, index) => (
                <Alert key={index} className={getSeverityColor(indicator.severity)}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        {getSeverityBadge(indicator.severity)}
                        <span className="text-sm font-medium capitalize">{indicator.type.replace('_', ' ')}</span>
                      </div>
                      <AlertDescription>{indicator.description}</AlertDescription>
                      <div className="text-xs text-gray-500 mt-1">
                        Location: {indicator.location}
                      </div>
                    </div>
                  </div>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suspicious Regions */}
      {transactionAnalysis.suspicious_regions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5 text-orange-500" />
              <span>Suspicious Regions</span>
            </CardTitle>
            <CardDescription>
              Areas in the image that require closer inspection
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {transactionAnalysis.suspicious_regions.map((region, index) => (
                <div key={index} className="p-3 border rounded-lg bg-orange-50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium capitalize">{region.type.replace('_', ' ')}</span>
                    {region.confidence && (
                      <Badge variant="outline">{(region.confidence * 100).toFixed(1)}% confidence</Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{region.description}</p>
                  {region.location && (
                    <div className="text-xs text-gray-500">
                      Position: x:{region.location.x}, y:{region.location.y}
                      {region.size && ` | Size: ${region.size.width}x${region.size.height}px`}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Text Analysis */}
      {transactionAnalysis.text_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-blue-500" />
              <span>Text Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {transactionAnalysis.text_analysis.app_identified && (
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">Detected App:</span>
                <Badge variant="outline" className="capitalize">
                  {transactionAnalysis.text_analysis.app_identified.replace('_', ' ')}
                </Badge>
              </div>
            )}
            
            {transactionAnalysis.text_analysis.detected_amounts.length > 0 && (
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <DollarSign className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium">Detected Amounts:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {transactionAnalysis.text_analysis.detected_amounts.map((amount, index) => (
                    <Badge key={index} variant="outline" className="text-green-600">
                      {amount}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            
            {transactionAnalysis.text_analysis.detected_dates.length > 0 && (
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium">Detected Dates:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {transactionAnalysis.text_analysis.detected_dates.map((date, index) => (
                    <Badge key={index} variant="outline" className="text-blue-600">
                      {date}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {transactionAnalysis.text_analysis.text_anomalies.length > 0 && (
              <div>
                <span className="text-sm font-medium text-red-600 mb-2 block">Text Anomalies Found:</span>
                <div className="space-y-1">
                  {transactionAnalysis.text_analysis.text_anomalies.map((anomaly, index) => (
                    <Alert key={index} variant="destructive">
                      <AlertDescription>{anomaly}</AlertDescription>
                    </Alert>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Reverse Search Results */}
      {reverseSearch && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5 text-purple-500" />
              <span>Reverse Image Search</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {reverseSearch.found_matches ? (
              <div className="space-y-3">
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Similar images found online! This may indicate the image is not original.
                  </AlertDescription>
                </Alert>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Similar Images:</span> {reverseSearch.similar_images}
                  </div>
                  {reverseSearch.earliest_occurrence && (
                    <div>
                      <span className="font-medium">Earliest Found:</span> {reverseSearch.earliest_occurrence}
                    </div>
                  )}
                </div>
                {reverseSearch.warnings.map((warning, index) => (
                  <Alert key={index} variant="destructive">
                    <AlertDescription>{warning}</AlertDescription>
                  </Alert>
                ))}
              </div>
            ) : (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  No similar images found in online databases.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Metadata Analysis */}
      {transactionAnalysis.metadata_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="h-5 w-5 text-gray-500" />
              <span>Metadata Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">EXIF Data:</span> {transactionAnalysis.metadata_analysis.has_exif ? 'Present' : 'Missing'}
                </div>
                {transactionAnalysis.metadata_analysis.creation_date && (
                  <div>
                    <span className="font-medium">Created:</span> {transactionAnalysis.metadata_analysis.creation_date}
                  </div>
                )}
              </div>
              
              {transactionAnalysis.metadata_analysis.device_info && (
                <div>
                  <span className="font-medium">Device:</span> {transactionAnalysis.metadata_analysis.device_info}
                </div>
              )}
              
              {transactionAnalysis.metadata_analysis.software_used && (
                <div>
                  <span className="font-medium">Software:</span> {transactionAnalysis.metadata_analysis.software_used}
                </div>
              )}
              
              {transactionAnalysis.metadata_analysis.suspicious_metadata.length > 0 && (
                <div className="space-y-1">
                  <span className="font-medium text-red-600">Metadata Concerns:</span>
                  {transactionAnalysis.metadata_analysis.suspicious_metadata.map((concern, index) => (
                    <Alert key={index} variant="destructive">
                      <AlertDescription>{concern}</AlertDescription>
                    </Alert>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {transactionAnalysis.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-green-500" />
              <span>Recommendations</span>
            </CardTitle>
            <CardDescription>
              Steps to verify the authenticity of this transaction
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {transactionAnalysis.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start space-x-2 text-sm">
                  <span className="text-gray-400 mt-1">•</span>
                  <span className={recommendation.includes('HIGH RISK') ? 'text-red-600 font-medium' : 
                                 recommendation.includes('MODERATE RISK') ? 'text-yellow-600 font-medium' : ''}> 
                    {recommendation}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TransactionAnalysisResults;
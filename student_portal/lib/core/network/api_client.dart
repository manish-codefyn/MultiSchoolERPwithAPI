import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/constants.dart';

final apiClientProvider = Provider((ref) => ApiClient(ref));

class ApiClient {
  final Ref _ref;
  final Dio _dio;
  final _storage = const FlutterSecureStorage();

  ApiClient(this._ref)
      : _dio = Dio(BaseOptions(
          baseUrl: AppConstants.defaultBaseUrl,
          connectTimeout: const Duration(seconds: 15),
          receiveTimeout: const Duration(seconds: 15),
          contentType: 'application/json',
        )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add auth token if available
        final token = await _storage.read(key: AppConstants.tokenKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        
        // Add X-Tenant-ID header for tenant selection
        final tenantSchema = await _storage.read(key: AppConstants.tenantSchemaKey);
        if (tenantSchema != null) {
          options.headers[AppConstants.tenantIdKey] = tenantSchema;
        }
        
        return handler.next(options);
      },
      onError: (e, handler) {
        // Handle common errors like 401 Unauthorized
        if (e.response?.statusCode == 401) {
          // Trigger logout or refresh token logic if needed
        }
        return handler.next(e);
      },
    ));

    // Initialize base URL from storage
    _initBaseUrl();
  }

  void _initBaseUrl() async {
    final url = await _storage.read(key: AppConstants.tenantUrlKey);
    if (url != null) {
      String baseUrl = url.endsWith('/') ? url : '$url/';
      // Ensure it has api/v1/
      if (!baseUrl.contains('/api/v1/')) {
        baseUrl = '${baseUrl}api/v1/';
      }
      _dio.options.baseUrl = baseUrl;
    }
  }

  void setBaseUrl(String url) {
    String baseUrl = url.endsWith('/') ? url : '$url/';
    if (!baseUrl.contains('/api/v1/')) {
      baseUrl = '${baseUrl}api/v1/';
    }
    _dio.options.baseUrl = baseUrl;
    _storage.write(key: AppConstants.tenantUrlKey, value: baseUrl);
  }

  Dio get client => _dio;
}

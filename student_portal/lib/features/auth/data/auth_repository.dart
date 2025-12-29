import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../core/network/api_client.dart';
import '../../../core/config/constants.dart';
import '../../profile/models/student_profile.dart';

final authRepositoryProvider = Provider((ref) => AuthRepository(ref));

class AuthRepository {
  final Ref _ref;
  final _storage = const FlutterSecureStorage();

  AuthRepository(this._ref);

  Future<StudentProfile?> login(String email, String password) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final tenantSchema = await _storage.read(key: AppConstants.tenantSchemaKey);
      
      final response = await dio.post('auth/api-login/', data: {
        'email': email,
        'password': password,
        'tenant_schema': tenantSchema, 
      });

      final tokens = response.data['tokens'];
      await _storage.write(key: AppConstants.tokenKey, value: tokens['access']);
      await _storage.write(key: 'refresh_token', value: tokens['refresh']);
      
      // Fetch profile immediately after login to confirm it's a student
      return await getProfile();
    } catch (e) {
      rethrow;
    }
  }

  Future<StudentProfile?> getProfile() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/profile/');
      return StudentProfile.fromJson(response.data);
    } catch (e) {
      return null;
    }
  }

  Future<void> logout() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      await dio.post('auth/api-logout/');
    } catch (_) {}
    await _storage.delete(key: AppConstants.tokenKey);
    await _storage.delete(key: 'refresh_token');
  }

  Future<Map<String, dynamic>> checkTenant(String schema) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('public/lookup/', queryParameters: {'schema': schema});
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> saveTenant(String schema, String? url, String? name) async {
    await _storage.write(key: AppConstants.tenantSchemaKey, value: schema);
    if (url != null) {
      _ref.read(apiClientProvider).setBaseUrl(url);
    }
    if (name != null) {
      await _storage.write(key: AppConstants.tenantNameKey, value: name);
    }
  }

  Future<String?> getTenantName() async {
    return await _storage.read(key: AppConstants.tenantNameKey);
  }

  Future<bool> hasTenant() async {
    final schema = await _storage.read(key: AppConstants.tenantSchemaKey);
    return schema != null;
  }

  Future<bool> hasToken() async {
    final token = await _storage.read(key: AppConstants.tokenKey);
    return token != null;
  }
}

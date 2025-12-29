import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/dashboard_data.dart';

final dashboardRepositoryProvider = Provider((ref) => DashboardRepository(ref));

class DashboardRepository {
  final Ref _ref;

  DashboardRepository(this._ref);

  Future<DashboardData> getDashboardData() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/dashboard/');
      return DashboardData.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }
}

final dashboardDataProvider = FutureProvider<DashboardData>((ref) async {
  return ref.read(dashboardRepositoryProvider).getDashboardData();
});

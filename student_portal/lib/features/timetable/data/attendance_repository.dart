import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/attendance.dart';

final attendanceRepositoryProvider = Provider((ref) => AttendanceRepository(ref));

class AttendanceRepository {
  final Ref _ref;

  AttendanceRepository(this._ref);

  Future<List<Attendance>> getAttendance() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/attendance/');
      final dynamic data = response.data;
      
      // Handle potential pagination and null results
      final List results = (data is Map) ? (data['results'] ?? []) : (data ?? []);
      
      return results.map((e) => Attendance.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }
}

final attendanceProvider = FutureProvider<List<Attendance>>((ref) async {
  return ref.read(attendanceRepositoryProvider).getAttendance();
});

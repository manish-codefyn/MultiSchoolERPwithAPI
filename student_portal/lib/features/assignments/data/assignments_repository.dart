import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/assignment.dart';

final assignmentsRepositoryProvider = Provider((ref) => AssignmentsRepository(ref));

class AssignmentsRepository {
  final Ref _ref;

  AssignmentsRepository(this._ref);

  Future<Map<String, dynamic>> getCategorizedAssignments() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/assignments/');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<Assignment> getAssignmentDetail(String id) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/assignments/$id/');
      return Assignment.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> submitAssignment({
    required String assignmentId,
    String? text,
    String? filePath,
  }) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final formData = FormData.fromMap({
        if (text != null) 'submission_text': text,
        if (filePath != null)
          'submission_file': await MultipartFile.fromFile(
            filePath,
            filename: filePath.split('/').last,
          ),
      });

      await dio.post('student-portal/assignments/$assignmentId/submit/', data: formData);
    } catch (e) {
      rethrow;
    }
  }
}

final categorizedAssignmentsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return ref.read(assignmentsRepositoryProvider).getCategorizedAssignments();
});

final assignmentDetailProvider = FutureProvider.family<Assignment, String>((ref, id) async {
  return ref.read(assignmentsRepositoryProvider).getAssignmentDetail(id);
});

import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/auth_repository.dart';
import '../../profile/models/student_profile.dart';

final authControllerProvider = AsyncNotifierProvider<AuthController, StudentProfile?>(AuthController.new);

class AuthController extends AsyncNotifier<StudentProfile?> {
  @override
  FutureOr<StudentProfile?> build() async {
    final repo = ref.read(authRepositoryProvider);
    if (await repo.hasToken() && await repo.hasTenant()) {
      try {
        return await repo.getProfile();
      } catch (e) {
        // If token is invalid or expired, clear it
        await repo.logout();
        return null;
      }
    }
    return null;
  }

  Future<void> login(String email, String password) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final profile = await ref.read(authRepositoryProvider).login(email, password);
      return profile;
    });
  }

  Future<void> logout() async {
    state = const AsyncLoading();
    await ref.read(authRepositoryProvider).logout();
    state = const AsyncValue.data(null);
  }
}

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/auth_controller.dart';
import '../../features/auth/data/auth_repository.dart';
import '../../features/dashboard/presentation/dashboard_screen.dart';
import '../../features/assignments/presentation/assignments_list_screen.dart';
import '../../features/assignments/presentation/assignment_detail_screen.dart';
import '../../features/finance/presentation/invoice_list_screen.dart';
import '../../features/finance/presentation/invoice_detail_screen.dart';
import '../../features/timetable/presentation/timetable_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/communications/presentation/inbox_screen.dart';
import '../../features/communications/presentation/thread_screen.dart';
import '../../features/tenant/presentation/tenant_selection_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authControllerProvider);
  final authRepo = ref.read(authRepositoryProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) async {
      final matched = state.matchedLocation;
      
      // 1. Check if tenant is selected
      final hasTenant = await authRepo.hasTenant();
      if (!hasTenant && matched != '/tenant') {
        return '/tenant';
      }
      
      if (authState.isLoading) return null;

      // 2. Check auth
      final loggedIn = authState.value != null;
      if (!loggedIn && matched != '/login' && matched != '/tenant') {
        return '/login';
      }
      
      if (loggedIn && (matched == '/login' || matched == '/tenant')) {
        return '/';
      }
      
      return null;
    },
    routes: [
      GoRoute(
        path: '/tenant',
        builder: (context, state) => const TenantSelectionScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/assignments',
        builder: (context, state) => const AssignmentsListScreen(),
        routes: [
          GoRoute(
            path: ':id',
            builder: (context, state) => AssignmentDetailScreen(id: state.pathParameters['id']!),
          ),
        ],
      ),
      GoRoute(
        path: '/finance',
        builder: (context, state) => const InvoiceListScreen(),
        routes: [
          GoRoute(
            path: ':id',
            builder: (context, state) => InvoiceDetailScreen(id: state.pathParameters['id']!),
          ),
        ],
      ),
      GoRoute(
        path: '/timetable',
        builder: (context, state) => const TimetableScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/messages',
        builder: (context, state) => const InboxScreen(),
        routes: [
          GoRoute(
            path: ':id',
            builder: (context, state) => ThreadScreen(id: state.pathParameters['id']!),
          ),
        ],
      ),
    ],
  );
});

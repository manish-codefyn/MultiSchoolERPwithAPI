import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/dashboard_repository.dart';
import '../../auth/presentation/auth_controller.dart';
import '../../../core/theme/app_theme.dart';
import 'package:intl/intl.dart';
import 'package:cached_network_image/cached_network_image.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardAsync = ref.watch(dashboardDataProvider);
    final profile = ref.watch(authControllerProvider).value;

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(dashboardDataProvider.future),
        child: CustomScrollView(
          slivers: [
            // App Bar with Profile
            SliverAppBar(
              expandedHeight: 200,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [AppTheme.primaryBlue, AppTheme.secondaryBlue],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                radius: 28,
                                backgroundColor: Colors.white24,
                                child: ClipOval(
                                  child: profile?.photoUrl != null
                                      ? CachedNetworkImage(
                                          imageUrl: profile!.photoUrl!,
                                          width: 56,
                                          height: 56,
                                          fit: BoxFit.cover,
                                          placeholder: (context, url) => const CircularProgressIndicator(strokeWidth: 2),
                                          errorWidget: (context, url, error) => const Icon(Icons.person, color: Colors.white, size: 30),
                                        )
                                      : const Icon(Icons.person, color: Colors.white, size: 30),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Welcome back,',
                                      style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 16),
                                    ),
                                    Text(
                                      profile?.fullName ?? 'Student',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 22,
                                        fontWeight: FontWeight.bold,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            decoration: BoxDecoration(
                              color: Colors.white24,
                              borderRadius: BorderRadius.circular(30),
                            ),
                            child: Text(
                              '${profile?.className ?? "Class"} - ${profile?.sectionName ?? "Section"}',
                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              actions: [
                IconButton(
                  icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                  onPressed: () => context.push('/notifications'),
                ),
                IconButton(
                  icon: const Icon(Icons.logout, color: Colors.white),
                  onPressed: () => ref.read(authControllerProvider.notifier).logout(),
                ),
              ],
            ),

            // Content
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Stats Row
                    dashboardAsync.when(
                      data: (data) => Row(
                        children: [
                          Expanded(
                            child: _StatCard(
                              title: 'Pending Fees',
                              value: '₹${data.pendingFees}',
                              icon: Icons.account_balance_wallet_outlined,
                              color: AppTheme.danger,
                              onTap: () => context.push('/finance'),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _StatCard(
                              title: 'Due Tasks',
                              value: '${data.upcomingAssignments.length}',
                              icon: Icons.assignment_outlined,
                              color: AppTheme.warning,
                              onTap: () => context.push('/assignments'),
                            ),
                          ),
                        ],
                      ),
                      loading: () => const Row(
                        children: [
                          Expanded(child: _StatCardPlaceholder()),
                          SizedBox(width: 16),
                          Expanded(child: _StatCardPlaceholder()),
                        ],
                      ),
                      error: (_, __) => const SizedBox.shrink(),
                    ),
                    const SizedBox(height: 32),

                    // Quick Links Grid
                    const Text(
                      'Quick Links',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    GridView.count(
                      crossAxisCount: 3,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      mainAxisSpacing: 16,
                      crossAxisSpacing: 16,
                      children: [
                        _QuickLink(
                          icon: Icons.schedule_rounded,
                          label: 'Timetable',
                          color: Colors.blue,
                          onTap: () => context.push('/timetable'),
                        ),
                        _QuickLink(
                          icon: Icons.assignment_rounded,
                          label: 'Assignments',
                          color: Colors.purple,
                          onTap: () => context.push('/assignments'),
                        ),
                        _QuickLink(
                          icon: Icons.account_balance_wallet_rounded,
                          label: 'Fees',
                          color: Colors.orange,
                          onTap: () => context.push('/finance'),
                        ),
                        _QuickLink(
                          icon: Icons.person_rounded,
                          label: 'Profile',
                          color: Colors.teal,
                          onTap: () => context.push('/profile'),
                        ),
                        _QuickLink(
                          icon: Icons.chat_rounded,
                          label: 'Messages',
                          color: Colors.green,
                          onTap: () => context.push('/messages'),
                        ),
                        _QuickLink(
                          icon: Icons.videogame_asset_rounded,
                          label: 'Games',
                          color: Colors.indigo,
                          onTap: () => context.push('/games'),
                        ),
                        _QuickLink(
                          icon: Icons.event_note_rounded,
                          label: 'Attendance',
                          color: Colors.redAccent,
                          onTap: () => context.push('/attendance'),
                        ),
                        _QuickLink(
                          icon: Icons.hotel,
                          label: 'Hostel',
                          color: Colors.brown,
                          onTap: () => context.push('/hostel'),
                        ),
                        _QuickLink(
                          icon: Icons.assignment_turned_in_rounded,
                          label: 'Exams',
                          color: Colors.deepOrange,
                          onTap: () => context.push('/exams'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),

                    // Upcoming Assignments
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Upcoming Assignments',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                        TextButton(
                          onPressed: () => context.push('/assignments'),
                          child: const Text('See All'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    dashboardAsync.when(
                      data: (data) => data.upcomingAssignments.isEmpty
                          ? const Center(child: Text('No upcoming assignments'))
                          : Column(
                              children: data.upcomingAssignments.map((a) => _AssignmentListTile(assignment: a)).toList(),
                            ),
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (e, __) => Center(child: Text('Error: $e')),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(height: 12),
              Text(
                value,
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              Text(
                title,
                style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatCardPlaceholder extends StatelessWidget {
  const _StatCardPlaceholder();
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(16),
      ),
    );
  }
}

class _QuickLink extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickLink({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(icon, color: color, size: 30),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _AssignmentListTile extends StatelessWidget {
  final dynamic assignment; // Should be Assignment model
  const _AssignmentListTile({required this.assignment});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppTheme.primaryBlue.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.edit_note_rounded, color: AppTheme.primaryBlue),
        ),
        title: Text(
          assignment.title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text('${assignment.subjectName} • Due ${DateFormat('dd MMM').format(DateTime.parse(assignment.dueDate))}'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => context.push('/assignments/${assignment.id}'),
      ),
    );
  }
}

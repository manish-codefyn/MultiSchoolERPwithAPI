import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../auth/presentation/auth_controller.dart';
import '../../../core/theme/app_theme.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(authControllerProvider).value;

    if (profile == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () {}, // Future: Edit Profile
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Profile Header
            Center(
              child: Column(
                children: [
                  Stack(
                    children: [
                      CircleAvatar(
                        radius: 60,
                        backgroundColor: AppTheme.primaryBlue.withOpacity(0.1),
                        backgroundImage: profile.photoUrl != null ? NetworkImage(profile.photoUrl!) : null,
                        child: profile.photoUrl == null 
                            ? const Icon(Icons.person, size: 60, color: AppTheme.primaryBlue) 
                            : null,
                      ),
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(color: AppTheme.primaryBlue, shape: BoxShape.circle),
                          child: const Icon(Icons.camera_alt, color: Colors.white, size: 20),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    profile.fullName,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'Admission No: ${profile.admissionNumber ?? 'N/A'}',
                    style: const TextStyle(color: AppTheme.textMuted),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 40),

            // Academic Info
            _ProfileSection(
              title: 'Academic Information',
              children: [
                _ProfileTile(label: 'Class', value: profile.className ?? 'N/A', icon: Icons.class_outlined),
                _ProfileTile(label: 'Section', value: profile.sectionName ?? 'N/A', icon: Icons.grid_view_outlined),
                _ProfileTile(label: 'Roll Number', value: profile.rollNumber ?? 'N/A', icon: Icons.numbers_outlined),
                _ProfileTile(label: 'Status', value: profile.status, icon: Icons.info_outline),
              ],
            ),
            const SizedBox(height: 24),

            // Personal Info
            _ProfileSection(
              title: 'Personal Information',
              children: [
                _ProfileTile(label: 'Gender', value: profile.gender ?? 'N/A', icon: Icons.person_outline),
                _ProfileTile(label: 'Date of Birth', value: profile.dateOfBirth ?? 'N/A', icon: Icons.cake_outlined),
                _ProfileTile(label: 'Blood Group', value: profile.bloodGroup ?? 'N/A', icon: Icons.bloodtype_outlined),
              ],
            ),
            const SizedBox(height: 24),

            // Contact Info
            _ProfileSection(
              title: 'Contact Information',
              children: [
                _ProfileTile(label: 'Email', value: profile.email ?? 'N/A', icon: Icons.email_outlined),
                _ProfileTile(label: 'Phone', value: profile.phone ?? 'N/A', icon: Icons.phone_outlined),
              ],
            ),
            
            const SizedBox(height: 48),
            
            // Logout Button
            OutlinedButton.icon(
              onPressed: () => ref.read(authControllerProvider.notifier).logout(),
              icon: const Icon(Icons.logout, color: AppTheme.danger),
              label: const Text('Logout', style: TextStyle(color: AppTheme.danger)),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: AppTheme.danger),
                minimumSize: const Size.fromHeight(50),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _ProfileSection extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _ProfileSection({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Card(
          child: Column(children: children),
        ),
      ],
    );
  }
}

class _ProfileTile extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _ProfileTile({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: AppTheme.primaryBlue, size: 20),
      title: Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
      subtitle: Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
      dense: true,
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'auth_controller.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../core/config/constants.dart';
import '../../../core/theme/app_theme.dart';
import '../data/auth_repository.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _onLogin() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter email and password')),
      );
      return;
    }

    await ref.read(authControllerProvider.notifier).login(email, password);
    
    if (ref.read(authControllerProvider).hasValue && ref.read(authControllerProvider).value != null) {
      if (mounted) context.go('/');
    } else if (ref.read(authControllerProvider).hasError) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(ref.read(authControllerProvider).error.toString())),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppTheme.primaryBlue,
              AppTheme.secondaryBlue.withOpacity(0.8),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                   // Logo/Icon
                   Container(
                     padding: const EdgeInsets.all(20),
                     decoration: BoxDecoration(
                       color: Colors.white.withOpacity(0.2),
                       shape: BoxShape.circle,
                     ),
                     child: const Icon(
                       Icons.school_rounded,
                       size: 80,
                       color: Colors.white,
                     ),
                   ),
                   const SizedBox(height: 24),
                   const Text(
                     'Student Portal',
                     style: TextStyle(
                       fontSize: 32,
                       fontWeight: FontWeight.bold,
                       color: Colors.white,
                     ),
                   ),
                   const Text(
                     'Empowering your education',
                     style: TextStyle(
                       fontSize: 16,
                       color: Colors.white70,
                     ),
                   ),
                   const SizedBox(height: 48),
                   
                   // Login Card
                   Card(
                     elevation: 8,
                     shadowColor: Colors.black26,
                     shape: RoundedRectangleBorder(
                       borderRadius: BorderRadius.circular(24),
                     ),
                     child: Padding(
                       padding: const EdgeInsets.all(32.0),
                       child: Column(
                         crossAxisAlignment: CrossAxisAlignment.stretch,
                         children: [
                            FutureBuilder<String?>(
                              future: ref.read(authRepositoryProvider).getTenantName(),
                              builder: (context, snapshot) {
                                if (snapshot.hasData && snapshot.data != null) {
                                  return Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        snapshot.data!,
                                        style: const TextStyle(
                                          fontSize: 24,
                                          fontWeight: FontWeight.bold,
                                          color: AppTheme.primaryBlue,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      InkWell(
                                        onTap: () {
                                          // Clear tenant and go back
                                          const storage = FlutterSecureStorage();
                                          storage.delete(key: AppConstants.tenantSchemaKey);
                                          storage.delete(key: AppConstants.tenantNameKey);
                                          context.go('/tenant');
                                        },
                                        child: const Text(
                                          'Change School',
                                          style: TextStyle(
                                            color: AppTheme.secondaryBlue,
                                            fontSize: 12,
                                            fontWeight: FontWeight.w600,
                                            decoration: TextDecoration.underline,
                                          ),
                                        ),
                                      ),
                                    ],
                                  );
                                }
                                return const Text(
                                  'Welcome Back!',
                                  style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                  ),
                                );
                              },
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Sign in to your student account',
                              style: TextStyle(
                                color: Colors.grey[600],
                              ),
                            ),
                            const SizedBox(height: 32),
                           
                           // Email Field
                           TextField(
                             controller: _emailController,
                             decoration: InputDecoration(
                               labelText: 'Email Address',
                               prefixIcon: const Icon(Icons.email_outlined),
                               filled: true,
                               fillColor: Colors.grey[50],
                             ),
                           ),
                           const SizedBox(height: 20),
                           
                           // Password Field
                           TextField(
                             controller: _passwordController,
                             obscureText: _obscurePassword,
                             decoration: InputDecoration(
                               labelText: 'Password',
                               prefixIcon: const Icon(Icons.lock_outline),
                               suffixIcon: IconButton(
                                 icon: Icon(
                                   _obscurePassword ? Icons.visibility_off : Icons.visibility,
                                 ),
                                 onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                               ),
                               filled: true,
                               fillColor: Colors.grey[50],
                             ),
                           ),
                           const SizedBox(height: 12),
                           
                           // Forgot Password
                           Align(
                             alignment: Alignment.centerRight,
                             child: TextButton(
                               onPressed: () {},
                               child: const Text('Forgot Password?'),
                             ),
                           ),
                           const SizedBox(height: 32),
                           
                           // Login Button
                           ElevatedButton(
                             onPressed: authState.isLoading ? null : _onLogin,
                             style: ElevatedButton.styleFrom(
                               padding: const EdgeInsets.symmetric(vertical: 16),
                               shape: RoundedRectangleBorder(
                                 borderRadius: BorderRadius.circular(16),
                               ),
                             ),
                             child: authState.isLoading
                                 ? const SizedBox(
                                     height: 20,
                                     width: 20,
                                     child: CircularProgressIndicator(
                                       strokeWidth: 2,
                                       color: Colors.white,
                                     ),
                                   )
                                 : const Text(
                                     'Sign In',
                                     style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                                   ),
                           ),
                         ],
                       ),
                     ),
                   ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

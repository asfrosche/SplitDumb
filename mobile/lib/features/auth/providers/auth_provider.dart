import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/user.dart';
import '../../../core/network/api_client.dart';
import 'dart:convert';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(apiClientProvider));
});

class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;

  AuthState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  bool get isAuthenticated => user != null;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _apiClient;

  AuthNotifier(this._apiClient) : super(AuthState()) {
    _loadUser();
  }

  Future<void> _loadUser() async {
    try {
      final response = await _apiClient.get('/users/me');
      if (response.statusCode == 200) {
        final user = User.fromJson(response.data);
        state = AuthState(user: user);
      }
    } catch (e) {
      // User not authenticated
      state = AuthState();
    }
  }

  Future<bool> login(String email, String password) async {
    state = AuthState(isLoading: true);
    try {
      final response = await _apiClient.post('/auth/login', data: {
        'email': email,
        'password': password,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        await _apiClient.saveToken(data['access_token']);
        final user = User.fromJson(data['user']);
        state = AuthState(user: user);
        return true;
      }
      state = AuthState(error: 'Login failed');
      return false;
    } catch (e) {
      state = AuthState(error: 'Login failed: ${e.toString()}');
      return false;
    }
  }

  Future<bool> register(String email, String password, String name) async {
    state = AuthState(isLoading: true);
    try {
      final response = await _apiClient.post('/auth/register', data: {
        'email': email,
        'password': password,
        'name': name,
      });

      if (response.statusCode == 201) {
        final data = response.data;
        await _apiClient.saveToken(data['access_token']);
        final user = User.fromJson(data['user']);
        state = AuthState(user: user);
        return true;
      }
      state = AuthState(error: 'Registration failed');
      return false;
    } catch (e) {
      state = AuthState(error: 'Registration failed: ${e.toString()}');
      return false;
    }
  }

  Future<void> logout() async {
    await _apiClient.clearToken();
    state = AuthState();
  }
}

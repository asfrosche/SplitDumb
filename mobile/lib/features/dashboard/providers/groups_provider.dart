import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/group.dart';
import '../../auth/providers/auth_provider.dart';

final groupsProvider = FutureProvider<List<Group>>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  final response = await apiClient.get('/groups');
  if (response.statusCode == 200) {
    final List<dynamic> data = response.data;
    return data.map((json) => Group.fromJson(json)).toList();
  }
  throw Exception('Failed to load groups');
});

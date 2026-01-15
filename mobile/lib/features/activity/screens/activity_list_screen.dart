import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../auth/providers/auth_provider.dart';

class ActivityListScreen extends ConsumerStatefulWidget {
  final int groupId;

  const ActivityListScreen({super.key, required this.groupId});

  @override
  ConsumerState<ActivityListScreen> createState() => _ActivityListScreenState();
}

class _ActivityListScreenState extends ConsumerState<ActivityListScreen> {
  List<dynamic> _activities = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadActivities();
  }

  Future<void> _loadActivities() async {
    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.get('/groups/${widget.groupId}/activity');
      if (response.statusCode == 200) {
        setState(() {
          _activities = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  String _formatActivityType(String type) {
    switch (type) {
      case 'expense_created':
        return 'Expense added';
      case 'expense_updated':
        return 'Expense updated';
      case 'expense_deleted':
        return 'Expense deleted';
      case 'settlement_created':
        return 'Settlement recorded';
      default:
        return type;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Activity')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadActivities,
              child: _activities.isEmpty
                  ? const Center(child: Text('No activity yet'))
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _activities.length,
                      itemBuilder: (context, index) {
                        final activity = _activities[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ListTile(
                            title: Text(_formatActivityType(activity['type'])),
                            subtitle: Text(
                              DateFormat.yMMMd().add_jm().format(
                                    DateTime.parse(activity['created_at']),
                                  ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}

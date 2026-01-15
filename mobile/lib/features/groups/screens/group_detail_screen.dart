import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../core/network/api_client.dart';

class GroupDetailScreen extends ConsumerStatefulWidget {
  final int groupId;

  const GroupDetailScreen({super.key, required this.groupId});

  @override
  ConsumerState<GroupDetailScreen> createState() => _GroupDetailScreenState();
}

class _GroupDetailScreenState extends ConsumerState<GroupDetailScreen> {
  Map<String, dynamic>? _groupData;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadGroup();
  }

  Future<void> _loadGroup() async {
    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.get('/groups/${widget.groupId}');
      if (response.statusCode == 200) {
        setState(() {
          _groupData = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  String _formatCurrency(int cents, String currencyCode) {
    final amount = cents / 100;
    return NumberFormat.currency(symbol: _getCurrencySymbol(currencyCode)).format(amount);
  }

  String _getCurrencySymbol(String code) {
    const symbols = {'USD': '\$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'INR': '₹'};
    return symbols[code] ?? code;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null || _groupData == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Group')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $_error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isLoading = true;
                    _error = null;
                  });
                  _loadGroup();
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    final group = _groupData!['group'];
    final balances = _groupData!['balances'] as Map<String, dynamic>;
    final userBalance = _groupData!['user_balance'] as Map<String, dynamic>;

    return Scaffold(
      appBar: AppBar(
        title: Text(group['name']),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              context.go('/groups/${widget.groupId}/activity');
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadGroup,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Balance summary
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Your Balance',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      ...userBalance.entries.map((entry) {
                        final balance = entry.value as int;
                        final color = balance >= 0 ? Colors.green : Colors.red;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(entry.key),
                              Text(
                                _formatCurrency(balance.abs(), entry.key),
                                style: TextStyle(
                                  color: color,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // All balances
              const Text(
                'All Balances',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...balances.entries.map((currencyEntry) {
                final currencyCode = currencyEntry.key;
                final userBalances = currencyEntry.value as Map<String, dynamic>;
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          currencyCode,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        ...userBalances.entries.map((entry) {
                          final balance = entry.value as int;
                          if (balance == 0) return const SizedBox.shrink();
                          final color = balance >= 0 ? Colors.green : Colors.red;
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text('User ${entry.key}'),
                                Text(
                                  _formatCurrency(balance.abs(), currencyCode),
                                  style: TextStyle(color: color),
                                ),
                              ],
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                );
              }),
            ],
          ),
        ),
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            heroTag: 'settle',
            onPressed: () {
              context.go('/groups/${widget.groupId}/settle');
            },
            child: const Icon(Icons.payment),
          ),
          const SizedBox(height: 16),
          FloatingActionButton(
            heroTag: 'add',
            onPressed: () {
              context.go('/groups/${widget.groupId}/expenses/add');
            },
            child: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/models/group.dart';

class SettleUpScreen extends ConsumerStatefulWidget {
  final int groupId;

  const SettleUpScreen({super.key, required this.groupId});

  @override
  ConsumerState<SettleUpScreen> createState() => _SettleUpScreenState();
}

class _SettleUpScreenState extends ConsumerState<SettleUpScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  int? _selectedToUserId;
  Group? _group;
  Map<String, dynamic>? _balances;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final apiClient = ref.read(apiClientProvider);
      final groupResponse = await apiClient.get('/groups/${widget.groupId}');
      if (groupResponse.statusCode == 200) {
        setState(() {
          _group = Group.fromJson(groupResponse.data['group']);
          _balances = groupResponse.data['balances'];
        });
      }
    } catch (e) {
      // Handle error
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  Future<void> _submitSettlement() async {
    if (!_formKey.currentState!.validate() || _selectedToUserId == null) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final amountCents = (double.parse(_amountController.text) * 100).toInt();

      // Get current user ID from auth
      final authState = ref.read(authProvider);
      final fromUserId = authState.user?.id;

      if (fromUserId == null) {
        throw Exception('User not authenticated');
      }

      final settlementData = {
        'from_user_id': fromUserId,
        'to_user_id': _selectedToUserId,
        'amount_cents': amountCents,
        'currency_code': _group?.defaultCurrency ?? 'USD',
      };

      final response = await apiClient.post(
        '/groups/${widget.groupId}/settlements',
        data: settlementData,
      );

      if (response.statusCode == 201 && mounted) {
        context.pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Settlement recorded successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to record settlement: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_group == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Settle Up')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Who are you paying?',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              ...(_group!.members.map((member) {
                return RadioListTile<int>(
                  title: Text(member.user.name),
                  value: member.userId,
                  groupValue: _selectedToUserId,
                  onChanged: (value) {
                    setState(() {
                      _selectedToUserId = value;
                    });
                  },
                );
              })),
              const SizedBox(height: 24),
              TextFormField(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  labelText: 'Amount',
                  hintText: '0.00',
                  prefixText: _group?.defaultCurrency == 'USD' ? '\$' : '',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an amount';
                  }
                  if (double.tryParse(value) == null) {
                    return 'Please enter a valid number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _submitSettlement,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator()
                    : const Text('Record Settlement'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

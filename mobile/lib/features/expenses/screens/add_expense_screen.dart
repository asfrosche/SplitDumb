import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/models/group.dart';

class AddExpenseScreen extends ConsumerStatefulWidget {
  final int groupId;

  const AddExpenseScreen({super.key, required this.groupId});

  @override
  ConsumerState<AddExpenseScreen> createState() => _AddExpenseScreenState();
}

class _AddExpenseScreenState extends ConsumerState<AddExpenseScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _amountController = TextEditingController();
  final _notesController = TextEditingController();
  String _splitMode = 'equal';
  List<int> _selectedParticipants = [];
  Group? _group;
  bool _isLoading = false;

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
          _group = Group.fromJson(response.data['group']);
        });
      }
    } catch (e) {
      // Handle error
    }
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    _amountController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _submitExpense() async {
    if (!_formKey.currentState!.validate() || _selectedParticipants.isEmpty) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final amountCents = (double.parse(_amountController.text) * 100).toInt();

      final splitData = {'participants': _selectedParticipants};

      final expenseData = {
        'payer_id': _group!.members.first.userId, // Default to first member
        'amount_cents': amountCents,
        'currency_code': _group!.defaultCurrency,
        'description': _descriptionController.text,
        'notes': _notesController.text.isEmpty ? null : _notesController.text,
        'split_mode': _splitMode,
        'split_data': splitData,
      };

      final response = await apiClient.post(
        '/groups/${widget.groupId}/expenses',
        data: expenseData,
      );

      if (response.statusCode == 201 && mounted) {
        context.pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Expense added successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add expense: $e')),
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
    return Scaffold(
      appBar: AppBar(title: const Text('Add Expense')),
      body: _group == null
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextFormField(
                      controller: _descriptionController,
                      decoration: const InputDecoration(
                        labelText: 'Description',
                        hintText: 'What was this expense for?',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter a description';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
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
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _notesController,
                      decoration: const InputDecoration(
                        labelText: 'Notes (optional)',
                      ),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Split Mode',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    RadioListTile<String>(
                      title: const Text('Equal'),
                      value: 'equal',
                      groupValue: _splitMode,
                      onChanged: (value) {
                        setState(() {
                          _splitMode = value!;
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Participants',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    ...(_group!.members.map((member) {
                      return CheckboxListTile(
                        title: Text(member.user.name),
                        value: _selectedParticipants.contains(member.userId),
                        onChanged: (checked) {
                          setState(() {
                            if (checked == true) {
                              _selectedParticipants.add(member.userId);
                            } else {
                              _selectedParticipants.remove(member.userId);
                            }
                          });
                        },
                      );
                    })),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: _isLoading ? null : _submitExpense,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: _isLoading
                          ? const CircularProgressIndicator()
                          : const Text('Add Expense'),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}

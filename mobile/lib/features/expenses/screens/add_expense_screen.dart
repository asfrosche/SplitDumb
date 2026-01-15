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

class ExpenseItem {
  final String description;
  final double amount;
  final String? categoryId;
  final String splitMode;
  final Map<String, dynamic> splitData;

  ExpenseItem({
    required this.description,
    required this.amount,
    this.categoryId,
    this.splitMode = 'equal',
    Map<String, dynamic>? splitData,
  }) : splitData = splitData ?? {};
}

class _AddExpenseScreenState extends ConsumerState<AddExpenseScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _amountController = TextEditingController();
  final _notesController = TextEditingController();
  final _categoryController = TextEditingController();

  String _splitMode = 'equal';
  int? _selectedPayerId;
  bool _useItems = false;
  List<ExpenseItem> _items = [];
  
  // Split data for whole expense
  List<int> _selectedParticipants = [];
  Map<int, double> _unequalSplits = {}; // user_id -> amount
  Map<int, int> _shareSplits = {}; // user_id -> shares
  Map<int, double> _percentSplits = {}; // user_id -> percent

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
          if (_group!.members.isNotEmpty) {
            _selectedPayerId = _group!.members.first.userId;
          }
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load group: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    _amountController.dispose();
    _notesController.dispose();
    _categoryController.dispose();
    for (var item in _items) {
      // Clean up item controllers if any
    }
    super.dispose();
  }

  void _addItem() {
    setState(() {
      _items.add(ExpenseItem(
        description: '',
        amount: 0,
        splitMode: 'equal',
      ));
    });
  }

  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
    });
  }

  Map<String, dynamic> _buildSplitData() {
    switch (_splitMode) {
      case 'equal':
        return {'participants': _selectedParticipants};
      case 'unequal':
        return {
          'splits': _unequalSplits.entries
              .map((e) => {
                    'user_id': e.key,
                    'amount_cents': (e.value * 100).toInt(),
                  })
              .toList(),
        };
      case 'shares':
        return {
          'shares': _shareSplits.entries
              .map((e) => {
                    'user_id': e.key,
                    'share_count': e.value,
                  })
              .toList(),
        };
      case 'percent':
        return {
          'percents': _percentSplits.entries
              .map((e) => {
                    'user_id': e.key,
                    'percent': e.value,
                  })
              .toList(),
        };
      default:
        return {'participants': _selectedParticipants};
    }
  }

  Future<void> _submitExpense() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_selectedPayerId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a payer')),
      );
      return;
    }

    if (_selectedParticipants.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one participant')),
      );
      return;
    }

    if (!_useItems) {
      // Validate whole expense split totals
      if (_splitMode == 'unequal') {
        final totalAmount = double.tryParse(_amountController.text) ?? 0;
        final splitTotal = _unequalSplits.values.fold(0.0, (sum, val) => sum + val);
        if ((splitTotal - totalAmount).abs() > 0.01) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Split total (\$${splitTotal.toStringAsFixed(2)}) must equal expense amount (\$${totalAmount.toStringAsFixed(2)})')),
          );
          return;
        }
      } else if (_splitMode == 'percent') {
        final percentTotal = _percentSplits.values.fold(0.0, (sum, val) => sum + val);
        if ((percentTotal - 100.0).abs() > 0.01) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Percentages must total 100%, currently: ${percentTotal.toStringAsFixed(2)}%')),
          );
          return;
        }
      }
    } else {
      // Validate items
      if (_items.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please add at least one item')),
        );
        return;
      }

      for (var i = 0; i < _items.length; i++) {
        final item = _items[i];
        if (item.description.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Item ${i + 1} must have a description')),
          );
          return;
        }
        if (item.amount <= 0) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Item ${i + 1} must have an amount > 0')),
          );
          return;
        }
      }
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final amountCents = _useItems
          ? _items.fold(0, (sum, item) => sum + (item.amount * 100).toInt())
          : (double.parse(_amountController.text) * 100).toInt();

      final expenseData = {
        'payer_id': _selectedPayerId,
        'amount_cents': amountCents,
        'currency_code': _group!.defaultCurrency,
        'description': _descriptionController.text,
        'notes': _notesController.text.isEmpty ? null : _notesController.text,
        'category_id': _categoryController.text.isEmpty ? null : int.tryParse(_categoryController.text),
        'split_mode': _useItems ? 'equal' : _splitMode, // If items, backend will use item splits
        'split_data': _useItems ? {'participants': _selectedParticipants} : _buildSplitData(),
        'items': _useItems
            ? _items.map((item) {
                return {
                  'description': item.description,
                  'amount_cents': (item.amount * 100).toInt(),
                  'category_id': item.categoryId != null ? int.tryParse(item.categoryId!) : null,
                };
              }).toList()
            : null,
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

  Widget _buildSplitModeSelection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
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
        RadioListTile<String>(
          title: const Text('Unequal'),
          value: 'unequal',
          groupValue: _splitMode,
          onChanged: (value) {
            setState(() {
              _splitMode = value!;
            });
          },
        ),
        RadioListTile<String>(
          title: const Text('By Shares'),
          value: 'shares',
          groupValue: _splitMode,
          onChanged: (value) {
            setState(() {
              _splitMode = value!;
            });
          },
        ),
        RadioListTile<String>(
          title: const Text('By Percent'),
          value: 'percent',
          groupValue: _splitMode,
          onChanged: (value) {
            setState(() {
              _splitMode = value!;
            });
          },
        ),
      ],
    );
  }

  Widget _buildParticipantsSelection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
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
                  // Initialize split values
                  if (_splitMode == 'unequal') {
                    _unequalSplits[member.userId] = 0;
                  } else if (_splitMode == 'shares') {
                    _shareSplits[member.userId] = 1;
                  } else if (_splitMode == 'percent') {
                    _percentSplits[member.userId] = 0;
                  }
                } else {
                  _selectedParticipants.remove(member.userId);
                  _unequalSplits.remove(member.userId);
                  _shareSplits.remove(member.userId);
                  _percentSplits.remove(member.userId);
                }
              });
            },
          );
        })),
      ],
    );
  }

  Widget _buildSplitConfiguration() {
    if (_selectedParticipants.isEmpty) {
      return const SizedBox.shrink();
    }

    final totalAmount = _useItems
        ? _items.fold(0.0, (sum, item) => sum + item.amount)
        : double.tryParse(_amountController.text) ?? 0;

    switch (_splitMode) {
      case 'unequal':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Split Amounts',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            ..._selectedParticipants.map((userId) {
              final member = _group!.members.firstWhere((m) => m.userId == userId);
              final controller = TextEditingController(
                text: _unequalSplits[userId]?.toString() ?? '0',
              );
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: TextFormField(
                  controller: controller,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: '${member.user.name} amount',
                    prefixText: _group?.defaultCurrency == 'USD' ? '\$' : '',
                  ),
                  onChanged: (value) {
                    final amount = double.tryParse(value) ?? 0;
                    setState(() {
                      _unequalSplits[userId] = amount;
                    });
                  },
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Required';
                    }
                    final amount = double.tryParse(value);
                    if (amount == null || amount < 0) {
                      return 'Invalid amount';
                    }
                    return null;
                  },
                ),
              );
            }),
            const SizedBox(height: 8),
            Text(
              'Total: ${_group?.defaultCurrency == 'USD' ? '\$' : ''}${_unequalSplits.values.fold(0.0, (sum, val) => sum + val).toStringAsFixed(2)} / ${totalAmount.toStringAsFixed(2)}',
              style: TextStyle(
                color: _unequalSplits.values.fold(0.0, (sum, val) => sum + val) == totalAmount
                    ? Colors.green
                    : Colors.red,
              ),
            ),
          ],
        );

      case 'shares':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Share Counts',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            ..._selectedParticipants.map((userId) {
              final member = _group!.members.firstWhere((m) => m.userId == userId);
              final controller = TextEditingController(
                text: _shareSplits[userId]?.toString() ?? '1',
              );
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: TextFormField(
                  controller: controller,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: '${member.user.name} shares',
                  ),
                  onChanged: (value) {
                    final shares = int.tryParse(value) ?? 1;
                    setState(() {
                      _shareSplits[userId] = shares;
                    });
                  },
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Required';
                    }
                    final shares = int.tryParse(value);
                    if (shares == null || shares < 1) {
                      return 'Must be at least 1';
                    }
                    return null;
                  },
                ),
              );
            }),
          ],
        );

      case 'percent':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Percentages',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            ..._selectedParticipants.map((userId) {
              final member = _group!.members.firstWhere((m) => m.userId == userId);
              final controller = TextEditingController(
                text: _percentSplits[userId]?.toString() ?? '0',
              );
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: TextFormField(
                  controller: controller,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: '${member.user.name} %',
                    suffixText: '%',
                  ),
                  onChanged: (value) {
                    final percent = double.tryParse(value) ?? 0;
                    setState(() {
                      _percentSplits[userId] = percent;
                    });
                  },
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Required';
                    }
                    final percent = double.tryParse(value);
                    if (percent == null || percent < 0 || percent > 100) {
                      return 'Must be 0-100';
                    }
                    return null;
                  },
                ),
              );
            }),
            const SizedBox(height: 8),
            Text(
              'Total: ${_percentSplits.values.fold(0.0, (sum, val) => sum + val).toStringAsFixed(2)}%',
              style: TextStyle(
                color: (_percentSplits.values.fold(0.0, (sum, val) => sum + val) - 100).abs() < 0.01
                    ? Colors.green
                    : Colors.red,
              ),
            ),
          ],
        );

      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildItemCard(int index, ExpenseItem item) {
    final itemController = TextEditingController(text: item.description);
    final amountController = TextEditingController(text: item.amount.toString());
    final categoryController = TextEditingController(text: item.categoryId ?? '');

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Item ${index + 1}',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: () => _removeItem(index),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: itemController,
              decoration: const InputDecoration(
                labelText: 'Item Description',
              ),
              onChanged: (value) {
                setState(() {
                  _items[index] = ExpenseItem(
                    description: value,
                    amount: _items[index].amount,
                    categoryId: _items[index].categoryId,
                    splitMode: _items[index].splitMode,
                    splitData: _items[index].splitData,
                  );
                });
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: amountController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'Amount',
                prefixText: _group?.defaultCurrency == 'USD' ? '\$' : '',
              ),
              onChanged: (value) {
                final amount = double.tryParse(value) ?? 0;
                setState(() {
                  _items[index] = ExpenseItem(
                    description: _items[index].description,
                    amount: amount,
                    categoryId: _items[index].categoryId,
                    splitMode: _items[index].splitMode,
                    splitData: _items[index].splitData,
                  );
                });
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: categoryController,
              decoration: const InputDecoration(
                labelText: 'Category ID (optional)',
              ),
              onChanged: (value) {
                setState(() {
                  _items[index] = ExpenseItem(
                    description: _items[index].description,
                    amount: _items[index].amount,
                    categoryId: value.isEmpty ? null : value,
                    splitMode: _items[index].splitMode,
                    splitData: _items[index].splitData,
                  );
                });
              },
            ),
            const SizedBox(height: 16),
            const Text(
              'Note: Item splits use equal split for all participants',
              style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic),
            ),
          ],
        ),
      ),
    );
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
                    // Payer Selection
                    DropdownButtonFormField<int>(
                      value: _selectedPayerId,
                      decoration: const InputDecoration(
                        labelText: 'Paid by',
                      ),
                      items: _group!.members.map((member) {
                        return DropdownMenuItem<int>(
                          value: member.userId,
                          child: Text(member.user.name),
                        );
                      }).toList(),
                      onChanged: (value) {
                        setState(() {
                          _selectedPayerId = value;
                        });
                      },
                      validator: (value) {
                        if (value == null) {
                          return 'Please select a payer';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Use Items Toggle
                    SwitchListTile(
                      title: const Text('Split by individual items'),
                      subtitle: const Text('Add multiple items with separate splits'),
                      value: _useItems,
                      onChanged: (value) {
                        setState(() {
                          _useItems = value;
                          if (value) {
                            _items = [];
                          }
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    if (!_useItems) ...[
                      // Whole Expense Mode
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
                      _buildSplitModeSelection(),
                      const SizedBox(height: 16),
                      _buildParticipantsSelection(),
                      if (_selectedParticipants.isNotEmpty) ...[
                        const SizedBox(height: 16),
                        _buildSplitConfiguration(),
                      ],
                    ] else ...[
                      // Items Mode
                      TextFormField(
                        controller: _descriptionController,
                        decoration: const InputDecoration(
                          labelText: 'Expense Description',
                          hintText: 'Overall description for all items',
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter a description';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Participants (applies to all items)',
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
                      const SizedBox(height: 16),
                      ..._items.asMap().entries.map((entry) {
                        return _buildItemCard(entry.key, entry.value);
                      }),
                      ElevatedButton.icon(
                        onPressed: _addItem,
                        icon: const Icon(Icons.add),
                        label: const Text('Add Item'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Category
                    TextFormField(
                      controller: _categoryController,
                      decoration: const InputDecoration(
                        labelText: 'Category ID (optional)',
                        hintText: 'Enter category ID if available',
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Notes
                    TextFormField(
                      controller: _notesController,
                      decoration: const InputDecoration(
                        labelText: 'Notes (optional)',
                      ),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 24),

                    // Submit Button
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

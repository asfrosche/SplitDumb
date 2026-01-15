import 'package:json_annotation/json_annotation.dart';
import 'user.dart';

part 'expense.g.dart';

@JsonSerializable()
class Expense {
  final int id;
  @JsonKey(name: 'group_id')
  final int? groupId;
  @JsonKey(name: 'payer_user_id')
  final int payerUserId;
  @JsonKey(name: 'amount_cents')
  final int amountCents;
  @JsonKey(name: 'currency_code')
  final String currencyCode;
  final String description;
  final String? notes;
  @JsonKey(name: 'category_id')
  final int? categoryId;
  @JsonKey(name: 'occurred_at')
  final DateTime occurredAt;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  final List<ExpenseSplit> splits;
  final List<ExpenseItem> items;
  final User payer;

  Expense({
    required this.id,
    this.groupId,
    required this.payerUserId,
    required this.amountCents,
    required this.currencyCode,
    required this.description,
    this.notes,
    this.categoryId,
    required this.occurredAt,
    required this.createdAt,
    required this.splits,
    required this.items,
    required this.payer,
  });

  factory Expense.fromJson(Map<String, dynamic> json) => _$ExpenseFromJson(json);
  Map<String, dynamic> toJson() => _$ExpenseToJson(this);
}

@JsonSerializable()
class ExpenseSplit {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'amount_cents')
  final int amountCents;
  @JsonKey(name: 'share_type')
  final String shareType;
  @JsonKey(name: 'share_value')
  final String? shareValue;

  ExpenseSplit({
    required this.id,
    required this.userId,
    required this.amountCents,
    required this.shareType,
    this.shareValue,
  });

  factory ExpenseSplit.fromJson(Map<String, dynamic> json) => _$ExpenseSplitFromJson(json);
  Map<String, dynamic> toJson() => _$ExpenseSplitToJson(this);
}

@JsonSerializable()
class ExpenseItem {
  final int id;
  final String description;
  @JsonKey(name: 'amount_cents')
  final int amountCents;
  @JsonKey(name: 'category_id')
  final int? categoryId;

  ExpenseItem({
    required this.id,
    required this.description,
    required this.amountCents,
    this.categoryId,
  });

  factory ExpenseItem.fromJson(Map<String, dynamic> json) => _$ExpenseItemFromJson(json);
  Map<String, dynamic> toJson() => _$ExpenseItemToJson(this);
}

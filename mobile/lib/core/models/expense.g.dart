// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'expense.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Expense _$ExpenseFromJson(Map<String, dynamic> json) => Expense(
      id: json['id'] as int,
      groupId: json['group_id'] as int?,
      payerUserId: json['payer_user_id'] as int,
      amountCents: json['amount_cents'] as int,
      currencyCode: json['currency_code'] as String,
      description: json['description'] as String,
      notes: json['notes'] as String?,
      categoryId: json['category_id'] as int?,
      occurredAt: DateTime.parse(json['occurred_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      splits: (json['splits'] as List<dynamic>)
          .map((e) => ExpenseSplit.fromJson(e as Map<String, dynamic>))
          .toList(),
      items: (json['items'] as List<dynamic>)
          .map((e) => ExpenseItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      payer: User.fromJson(json['payer'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ExpenseToJson(Expense instance) => <String, dynamic>{
      'id': instance.id,
      'group_id': instance.groupId,
      'payer_user_id': instance.payerUserId,
      'amount_cents': instance.amountCents,
      'currency_code': instance.currencyCode,
      'description': instance.description,
      'notes': instance.notes,
      'category_id': instance.categoryId,
      'occurred_at': instance.occurredAt.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
      'splits': instance.splits,
      'items': instance.items,
      'payer': instance.payer,
    };

ExpenseSplit _$ExpenseSplitFromJson(Map<String, dynamic> json) =>
    ExpenseSplit(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      amountCents: json['amount_cents'] as int,
      shareType: json['share_type'] as String,
      shareValue: json['share_value'] as String?,
    );

Map<String, dynamic> _$ExpenseSplitToJson(ExpenseSplit instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'amount_cents': instance.amountCents,
      'share_type': instance.shareType,
      'share_value': instance.shareValue,
    };

ExpenseItem _$ExpenseItemFromJson(Map<String, dynamic> json) => ExpenseItem(
      id: json['id'] as int,
      description: json['description'] as String,
      amountCents: json['amount_cents'] as int,
      categoryId: json['category_id'] as int?,
    );

Map<String, dynamic> _$ExpenseItemToJson(ExpenseItem instance) =>
    <String, dynamic>{
      'id': instance.id,
      'description': instance.description,
      'amount_cents': instance.amountCents,
      'category_id': instance.categoryId,
    };

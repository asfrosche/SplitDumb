import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/groups/screens/group_detail_screen.dart';
import '../../features/expenses/screens/add_expense_screen.dart';
import '../../features/expenses/screens/expense_detail_screen.dart';
import '../../features/settlements/screens/settle_up_screen.dart';
import '../../features/activity/screens/activity_list_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/groups/:groupId',
        builder: (context, state) {
          final groupId = int.parse(state.pathParameters['groupId']!);
          return GroupDetailScreen(groupId: groupId);
        },
      ),
      GoRoute(
        path: '/groups/:groupId/expenses/add',
        builder: (context, state) {
          final groupId = int.parse(state.pathParameters['groupId']!);
          return AddExpenseScreen(groupId: groupId);
        },
      ),
      GoRoute(
        path: '/expenses/:expenseId',
        builder: (context, state) {
          final expenseId = int.parse(state.pathParameters['expenseId']!);
          return ExpenseDetailScreen(expenseId: expenseId);
        },
      ),
      GoRoute(
        path: '/groups/:groupId/settle',
        builder: (context, state) {
          final groupId = int.parse(state.pathParameters['groupId']!);
          return SettleUpScreen(groupId: groupId);
        },
      ),
      GoRoute(
        path: '/groups/:groupId/activity',
        builder: (context, state) {
          final groupId = int.parse(state.pathParameters['groupId']!);
          return ActivityListScreen(groupId: groupId);
        },
      ),
    ],
  );
}

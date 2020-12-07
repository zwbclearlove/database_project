
#include <stdio.h>
#include <string.h>

enum
{
	plus = -2147483647, minus = -2147483646,
	mult = -2147483645, devide = -2147483644,
	mod = -2147483643, leftbk = -2147483642,
	rightbk = -2147483641, op = -2147483640
};
int calc[500],ans[4];
int opstack[500];
char formula[500];
int temp[500], formulalen = 0, calctick = 0;

void Initstack(int *top)
{
	*top = -1;
}

int isempty(int *top)
{
	return *top == -1;
}
int isfull(int *top)
{
	return *top == 499;
}
int gettops(int stack[], int *top, int *item)
{
	if (isfull(top))
	{
		return 0;
	}
	else
	{
		*item = stack[*top];
		return 1;
	}
}
int push(int stack[], int *top, int *item)
{
	if (isfull(top))
	{
		return 0;
	}
	else
	{
		stack[++(*top)] = *item;
		return 1;
	}
}
int pop(int stack[], int *top)
{
	if (isempty(top))
	{
		return 0;
	}
	else
	{
		(*top)--;
		return 1;
	}
}


int isop(int s)
{
	return s < op;
}
int isnum(char s)
{
	if (s <= '9'&&s >= '0')return 1;
	else return 0;
}

void del_space(char str[])
{
	int state = 0, i = 0, len = strlen(str);
	while (1)
	{
		for (i = 0; i < len; i++)
		{
			if (str[i] == ' ' || str[i] == '=')
			{
				state = 1;
				break;
			}
		}
		if (state == 1)
		{
			for (; i <= len; i++)
			{
				str[i] = str[i + 1];
			}
			state = 0;
		}
		else if (state == 0)break;
	}
}

void chartoint(char str[])
{
	int i = 0;
	for (i = 0; str[i] != '\0'; i++)
	{
		if (isnum(str[i]))
		{
			int k = i, j = 0;
			while (isnum(str[k]))k++, j++;
			for (; j > 0; j--)
			{
				temp[formulalen] = temp[formulalen] * 10 + str[i++] - '0';
			}
			formulalen++;
			i--;

		}
		else
		{
			if (str[i] == '+')temp[formulalen] = plus, formulalen++;
			else if (str[i] == '-')temp[formulalen] = minus, formulalen++;
			else if (str[i] == '*')temp[formulalen] = mult, formulalen++;
			else if (str[i] == '/')temp[formulalen] = devide, formulalen++;
			else if (str[i] == '%')temp[formulalen] = mod, formulalen++;
			else if (str[i] == '(')temp[formulalen] = leftbk, formulalen++;
			else if (str[i] == ')')temp[formulalen] = rightbk, formulalen++;
		}
	}
}

void process(char formula[])
{
	del_space(formula);
	chartoint(formula);
}

void midtosuf(int temp[])
{
	int optop, i, recop;
	Initstack(&optop);
	for (i = 0; i < formulalen; i++)
	{
		if (isop(temp[i])==0)calc[calctick++] = temp[i];
		else
		{
			if (temp[i] == leftbk)push(opstack, &optop, &temp[i]);
			else if (temp[i] == rightbk)
			{
				while (1)
				{
					gettops(opstack, &optop, &recop);
					if (recop == leftbk)
					{
						pop(opstack, &optop);
						break;
					}
					else
					{
						calc[calctick++] = recop;
						pop(opstack, &optop);
					}
				}
				
			}
			else if (temp[i] == plus || temp[i] == minus)
			{
				gettops(opstack, &optop, &recop);
				if (isempty(&optop) || recop == leftbk)push(opstack, &optop, &temp[i]);
				else
				{
					while (1)
					{
						gettops(opstack, &optop, &recop);
						if (isempty(&optop) || recop == leftbk)
						{
							break;
						}
						else
						{
							calc[calctick++] = recop;
							pop(opstack, &optop);
						}
					}
					push(opstack, &optop, &temp[i]);
				}
			}
			else if (temp[i] == mult || temp[i] == devide || temp[i] == mod)
			{
				gettops(opstack, &optop, &recop);
				if (isempty(&optop)||recop == plus || recop == minus|| recop == leftbk)push(opstack, &optop, &temp[i]);
				else
				{
					calc[calctick++] = recop;
					pop(opstack, &optop);
					push(opstack, &optop, &temp[i]);
				}
			}
		}
	}
	while (!isempty(&optop))
	{
		gettops(opstack, &optop, &recop);
		calc[calctick++] = recop;
		pop(opstack, &optop);
	}
}
int getans(int calc[],int calctick)
{
	int anstop,i=0,a,b,c;
	Initstack(&anstop);
	for(i=0;i<calctick;i++)
	{
		if(!isop(calc[i]))
		{
			push(ans,&anstop,&calc[i]);
		}
		else
		{
			switch(calc[i])
			{
				case plus :
						gettops(ans,&anstop,&a);pop(ans,&anstop);
						gettops(ans,&anstop,&b);pop(ans,&anstop);
						c=b+a;push(ans,&anstop,&c);break;
				case minus :
						gettops(ans,&anstop,&a);pop(ans,&anstop);
						gettops(ans,&anstop,&b);pop(ans,&anstop);
						c=b-a;push(ans,&anstop,&c);break;
				case mult :
						gettops(ans,&anstop,&a);pop(ans,&anstop);
						gettops(ans,&anstop,&b);pop(ans,&anstop);
						c=b*a;push(ans,&anstop,&c);break;
				case devide :
						gettops(ans,&anstop,&a);pop(ans,&anstop);
						gettops(ans,&anstop,&b);pop(ans,&anstop);
						c=b/a;push(ans,&anstop,&c);break;						
				case mod :
						gettops(ans,&anstop,&a);pop(ans,&anstop);
						gettops(ans,&anstop,&b);pop(ans,&anstop);
						c=b%a;push(ans,&anstop,&c);break;		
			}
		}
	}
	gettops(ans,&anstop,&a);return a;
}
int main()
{
	int i;
	char c;

	fgets(formula, 512, stdin);
	process(formula);
	puts(formula);
	midtosuf(temp);
	for (i = 0; i < formulalen; i++)printf("%d ", temp[i]);
	printf("\n");
	for (i = 0; i < calctick; i++)printf("%d ", calc[i]);
	printf("\n");
	printf("%d\n",getans(calc,calctick));
	return 0;

}


